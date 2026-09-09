"""
AIService: Core service layer for DishaAI LLM integration.
Supports Google Gemini, Groq, OpenAI, and any OpenAI-compatible provider.
Safely incorporates student context and recent conversation history.
Includes timeout enforcement, bounded retry with exponential backoff, and model fallback.
"""
import json
import logging
import time
from decouple import config

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for all AI service errors."""
    def __init__(self, message, code='ai_error', status_code=503):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class AIServiceConfigError(AIServiceError):
    def __init__(self, message="AI assistant is not configured with a valid API key."):
        super().__init__(message, code='config_error', status_code=500)


class AIServiceTimeoutError(AIServiceError):
    def __init__(self, message="AI service request timed out. Please try again."):
        super().__init__(message, code='timeout', status_code=504)


class AIServiceRateLimitError(AIServiceError):
    def __init__(self, message="AI rate limit reached. Please wait a moment before trying again."):
        super().__init__(message, code='rate_limit', status_code=429)


class AIServiceUnavailableError(AIServiceError):
    def __init__(self, message="AI service is currently experiencing high demand. Please try again shortly."):
        super().__init__(message, code='service_unavailable', status_code=503)


class AIService:
    """
    Encapsulates all AI/LLM interaction for the DishaAI assistant.
    Keeps view logic clean, enforces security, and isolates external API calls.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are DishaAI, an expert AI-powered Student Learning Assistant and Personalized "
        "Career & Education Advisor.\n\n"
        "Your mission is to guide students with personalized, context-aware learning assistance, "
        "bridge their skill gaps, recommend learning roadmaps, explain complex concepts with clarity, "
        "generate quizzes and practice exercises, review code, and prepare students for career milestones.\n\n"
        "Core behavioral guidelines:\n"
        "- Tailor your depth and terminology to the student's current proficiency level (see student context). If they already know Python at 80%, do not treat them as a complete novice—explain next-level concepts directly.\n"
        "- When asked 'How should I learn X?' or for learning advice: analyze what they already know vs their target career and skill gaps, provide a concrete sequence, estimate study time, suggest mini-projects, and explain WHY.\n"
        "- When explaining code or concepts: explain simply first, provide clean, working, modern code examples, explain step-by-step, and offer a mini practice challenge.\n"
        "- Support specialized student workflows upon request: concept explanations (beginner/intermediate/advanced), code debugging, quiz and flashcard generation, study plans, mock interview questions, and resume advice.\n"
        "- Ground your guidance in the Student Context below. Encourage their learning streak and praise their progress.\n"
        "- Format responses with clean GitHub-flavored markdown (bolding, clear bullet points, and code blocks with syntax highlighting)."
    )

    # Secondary fallback models if primary model is unavailable
    GEMINI_FALLBACK_MODELS = ['gemini-3.6-flash', 'gemini-flash-latest']

    def __init__(self):
        self.provider = config('AI_PROVIDER', default='').strip().lower()
        self.api_key = config('AI_API_KEY', default='').strip()
        self.model = config('AI_MODEL', default='').strip()
        self.base_url = config('AI_BASE_URL', default='').strip()
        try:
            self.timeout = int(config('AI_TIMEOUT', default=30))
        except (ValueError, TypeError):
            self.timeout = 30

        # Auto-detect provider if not explicitly specified
        if not self.provider:
            if self.api_key.startswith('AIza'):
                self.provider = 'gemini'
            elif self.api_key.startswith('gsk_'):
                self.provider = 'groq'
            elif self.api_key.startswith('sk-'):
                self.provider = 'openai'
            else:
                self.provider = 'gemini'

        if not self.model:
            if self.provider == 'gemini':
                self.model = 'gemini-3.6-flash'
            elif self.provider == 'groq':
                self.model = 'llama-3.1-8b-instant'
            else:
                self.model = 'gpt-4o-mini'

    def reload_config(self):
        """Reload configuration dynamically if environment changed."""
        if getattr(self, '_testing_override', False):
            return
        self.__init__()

    def get_student_context(self, user) -> str:
        """
        Safely extracts 360-degree student profile context:
        Identity, target career, verified skills & proficiencies, skill gaps,
        active roadmap progress, quiz performance, and gamification level.
        """
        if not user or not user.is_authenticated:
            return "No authenticated student profile available."

        context_lines = []

        # 1. Basic identity
        name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        if not name:
            name = getattr(user, 'username', 'Student')
        context_lines.append(f"Student Name: {name}")

        role = getattr(user, 'role', None)
        if role:
            context_lines.append(f"Role: {role}")

        # 2. Student Profile & Target Career
        try:
            profile = getattr(user, 'student_profile', None)
            if profile:
                if profile.target_career:
                    context_lines.append(f"Target Career Goal: {profile.target_career.title} (Field: {profile.target_career.career_field.name})")
                if profile.grade_or_class:
                    context_lines.append(f"Academic Level: {profile.grade_or_class}")
                if profile.school_or_college:
                    context_lines.append(f"Institution: {profile.school_or_college}")

                # Interests
                interests = [i.name for i in profile.interests.all()[:8]]
                if interests:
                    context_lines.append(f"Interests: {', '.join(interests)}")

                # Student Skills with exact percentage proficiencies
                skills = [
                    f"{s.skill.name}: {s.proficiency_score}%"
                    for s in profile.skills.select_related('skill').all()[:15]
                ]
                if skills:
                    context_lines.append(f"Current Skill Proficiencies: {', '.join(skills)}")
        except Exception as e:
            logger.debug("Could not load full student profile context: %s", e)

        # 3. Latest Skill Gap Analysis & Readiness
        try:
            gap_analysis = user.skill_gap_analyses.select_related('career_path').first()
            if gap_analysis:
                context_lines.append(
                    f"Career Readiness for {gap_analysis.career_path.title}: {gap_analysis.readiness_score}%"
                )
                if gap_analysis.priority_skills:
                    gap_strs = [
                        f"{g.get('name')}: gap {g.get('gap')}% (Required {g.get('required_proficiency')}%)"
                        for g in gap_analysis.priority_skills[:4]
                    ]
                    context_lines.append(f"Priority Skill Gaps to Bridge: {', '.join(gap_strs)}")
        except Exception as e:
            logger.debug("Could not load skill gap context: %s", e)

        # 4. Learning Roadmap Progress
        try:
            active_roadmap = user.roadmaps.select_related('career_path').first()
            if active_roadmap:
                current_item = active_roadmap.items.filter(status='in_progress').first()
                item_title = current_item.title if current_item else "Foundations"
                context_lines.append(
                    f"Current Roadmap: {active_roadmap.title} ({active_roadmap.overall_progress}% completed, Active Phase {active_roadmap.active_phase} - Current Task: '{item_title}')"
                )
        except Exception as e:
            logger.debug("Could not load roadmap context: %s", e)

        # 5. Quiz Performance & Course Progress
        try:
            recent_attempts = user.quiz_attempts.select_related('quiz').order_by('-started_at')[:3]
            if recent_attempts:
                att_parts = [f"{a.quiz.title} ({a.score}% - {'Passed' if a.passed else 'Needs Revision'})" for a in recent_attempts]
                context_lines.append(f"Recent Quiz Performance: {'; '.join(att_parts)}")

            enrolled = user.course_progress.select_related('course').filter(status='in_progress')[:3]
            if enrolled:
                enrolled_titles = [f"{p.course.title} ({p.progress_percent}%)" for p in enrolled]
                context_lines.append(f"Courses in Progress: {', '.join(enrolled_titles)}")
        except Exception as e:
            logger.debug("Could not load learning progress context: %s", e)

        # 6. Gamification Stats
        try:
            gamification = getattr(user, 'gamification', None)
            if gamification:
                context_lines.append(
                    f"Gamification: Level {gamification.level} ({gamification.level_title}), "
                    f"Total XP: {gamification.xp}, Active Streak: {gamification.current_streak} days"
                )
        except Exception as e:
            logger.debug("Could not load gamification context: %s", e)

        return "\n".join(context_lines) if context_lines else "No specific profile details recorded yet."


    def build_system_prompt(self, student_context: str) -> str:
        """Constructs the complete system prompt injecting real student context."""
        return (
            f"{self.DEFAULT_SYSTEM_PROMPT}\n\n"
            f"=== CURRENT AUTHENTICATED STUDENT CONTEXT ===\n"
            f"{student_context}\n"
            f"============================================\n"
            f"Use this student context naturally to provide tailored, personalized guidance "
            f"whenever relevant (e.g. when recommending next steps or courses), but do not "
            f"recite this raw context unprompted."
        )

    def get_recent_history(self, session, exclude_message_id=None, limit=10):
        """
        Fetches the last `limit` messages from the session in chronological order.
        """
        if not session:
            return []
        try:
            qs = session.messages.all()
            if exclude_message_id:
                qs = qs.exclude(id=exclude_message_id)
            messages = list(qs.order_by('-created_at')[:limit])
            messages.reverse()
            return messages
        except Exception as e:
            logger.error("Error retrieving recent messages: %s", e)
            return []

    def _http_post_json(self, url: str, headers: dict, payload: dict) -> dict:
        """
        Executes HTTP POST request with explicit timeout and safe error classification.
        """
        try:
            import requests
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()

            status = resp.status_code
            text = resp.text[:400]
            logger.warning("LLM provider returned HTTP %s: %s", status, text)

            if status == 429:
                raise AIServiceRateLimitError(f"Rate limit exceeded (HTTP 429).")
            elif status in (500, 502, 503, 504):
                raise AIServiceUnavailableError(f"Provider unavailable (HTTP {status}).")
            elif status in (401, 403):
                raise AIServiceConfigError(f"Authentication failure with provider (HTTP {status}).")
            elif status == 404:
                raise AIServiceError(f"Requested model endpoint not found (HTTP 404).", code='model_not_found', status_code=404)
            else:
                raise AIServiceError(f"LLM API error (HTTP {status}): {text}", code='provider_error', status_code=status)

        except (AIServiceError, AIServiceRateLimitError, AIServiceUnavailableError, AIServiceConfigError, AIServiceTimeoutError):
            raise
        except Exception as e:
            # Handle requests network exceptions
            err_name = type(e).__name__
            if 'Timeout' in err_name:
                logger.warning("LLM provider request timed out after %ss", self.timeout)
                raise AIServiceTimeoutError(f"Request timed out after {self.timeout}s.")
            elif 'Connection' in err_name:
                logger.warning("LLM provider network connection error: %s", e)
                raise AIServiceUnavailableError("Failed to connect to AI provider.")
            else:
                logger.error("Unexpected error during LLM HTTP call: %s", e)
                raise AIServiceError(f"Network error: {str(e)}", code='network_error', status_code=503)

    def _call_gemini_single_model(self, model_name: str, system_prompt: str, history: list, new_message: str) -> str:
        """Invokes a specific Gemini model endpoint."""
        clean_model = model_name.replace('models/', '')
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{clean_model}:generateContent?key={self.api_key}"
        )
        headers = {'Content-Type': 'application/json'}

        contents = []
        for msg in history:
            role = 'user' if msg.sender == 'user' else 'model'
            contents.append({'role': role, 'parts': [{'text': msg.message}]})

        contents.append({'role': 'user', 'parts': [{'text': new_message}]})

        payload = {
            'systemInstruction': {
                'parts': [{'text': system_prompt}]
            },
            'contents': contents,
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 1500,
            }
        }

        data = self._http_post_json(url, headers, payload)
        try:
            candidates = data.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    text = parts[0].get('text', '').strip()
                    if text:
                        return text
        except Exception as e:
            logger.error("Failed to parse Gemini response payload: %s", e)

        raise AIServiceError("Received empty or unrecognized response from Gemini.", code='empty_response')

    def _call_gemini(self, system_prompt: str, history: list, new_message: str) -> str:
        """
        Invokes Gemini with retries and automatic fallback to stable models if
        the primary model encounters high demand (503) or is deprecated (404).
        """
        models_to_try = [self.model]
        for fallback in self.GEMINI_FALLBACK_MODELS:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_exception = None

        for model_candidate in models_to_try:
            max_retries = 2  # up to 2 retries = 3 attempts total per model
            for attempt in range(max_retries + 1):
                try:
                    logger.info(
                        "Calling Gemini model=%s attempt=%d/%d timeout=%ds",
                        model_candidate, attempt + 1, max_retries + 1, self.timeout
                    )
                    reply = self._call_gemini_single_model(model_candidate, system_prompt, history, new_message)
                    return reply

                except (AIServiceRateLimitError, AIServiceUnavailableError, AIServiceTimeoutError) as exc:
                    last_exception = exc
                    logger.warning(
                        "Gemini model=%s attempt=%d failed with %s: %s",
                        model_candidate, attempt + 1, exc.code, exc.message
                    )
                    if attempt < max_retries:
                        sleep_time = 1.0 * (2 ** attempt)  # 1s, 2s
                        time.sleep(sleep_time)
                    else:
                        logger.info("Exhausted retries for model=%s, trying next candidate if available.", model_candidate)

                except AIServiceError as exc:
                    last_exception = exc
                    # If 404 (model deprecated/unavailable), immediately break to try next model candidate
                    if getattr(exc, 'status_code', 0) == 404:
                        logger.warning("Gemini model=%s returned 404, moving to fallback model.", model_candidate)
                        break
                    # For non-retryable errors (e.g. 400/401/403), do not retry
                    raise

        if last_exception:
            raise last_exception
        raise AIServiceUnavailableError("All Gemini model attempts failed.")

    def _call_openai_compatible(self, base_url: str, system_prompt: str, history: list, new_message: str) -> str:
        """
        Invokes OpenAI, Groq, or any OpenAI-compatible chat completions endpoint with retries.
        """
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }

        messages = [{'role': 'system', 'content': system_prompt}]
        for msg in history:
            role = 'user' if msg.sender == 'user' else 'assistant'
            messages.append({'role': role, 'content': msg.message})

        messages.append({'role': 'user', 'content': new_message})

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 1500,
        }

        max_retries = 2
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    "Calling %s model=%s attempt=%d/%d timeout=%ds",
                    self.provider, self.model, attempt + 1, max_retries + 1, self.timeout
                )
                data = self._http_post_json(url, headers, payload)
                choices = data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '').strip()
                    if content:
                        return content
                raise AIServiceError("Received empty response from LLM provider.", code='empty_response')

            except (AIServiceRateLimitError, AIServiceUnavailableError, AIServiceTimeoutError) as exc:
                last_exception = exc
                logger.warning(
                    "%s model=%s attempt=%d failed with %s: %s",
                    self.provider, self.model, attempt + 1, exc.code, exc.message
                )
                if attempt < max_retries:
                    time.sleep(1.0 * (2 ** attempt))
            except AIServiceError:
                raise

        if last_exception:
            raise last_exception
        raise AIServiceUnavailableError(f"Failed to obtain response from {self.provider}.")

    def _generate_offline_fallback(self, user, new_message: str) -> str:
        """
        Generates an intelligent, context-grounded fallback response using real database
        data (target career, skill gaps, roadmap, gamification) when LLM provider is offline
        or unconfigured. Guarantees 100% uptime with zero crashes.
        """
        name = getattr(user, 'first_name', '') or getattr(user, 'username', 'Student')
        msg_lower = (new_message or '').lower().strip()

        # Gather real context
        target_career_title = "your chosen field"
        readiness_score = 0
        priority_gaps = []
        current_skills = []
        roadmap_title = ""
        roadmap_progress = 0

        try:
            profile = getattr(user, 'student_profile', None)
            if profile and profile.target_career:
                target_career_title = profile.target_career.title

            if profile:
                current_skills = [s.skill.name for s in profile.skills.select_related('skill').all()[:8]]

            gap_analysis = user.skill_gap_analyses.select_related('career_path').first()
            if gap_analysis:
                readiness_score = gap_analysis.readiness_score
                if gap_analysis.priority_skills:
                    priority_gaps = [g.get('name') for g in gap_analysis.priority_skills[:4] if g.get('name')]

            active_roadmap = user.roadmaps.select_related('career_path').first()
            if active_roadmap:
                roadmap_title = active_roadmap.title
                roadmap_progress = active_roadmap.overall_progress
        except Exception as e:
            logger.debug("Error collecting offline context: %s", e)

        # 1. Resume / ATS questions
        if any(w in msg_lower for w in ['resume', 'cv', 'ats', 'score', 'format']):
            gaps_txt = f", especially missing keywords like **{', '.join(priority_gaps)}**" if priority_gaps else ""
            return (
                f"### 📄 DishaAI Resume & ATS Advisory for **{name}**\n\n"
                f"To boost your ATS compatibility for **{target_career_title}** roles:\n\n"
                f"1. **Align Core Keywords**: Recruiters and ATS scanners match specific technical terms{gaps_txt}.\n"
                f"2. **Quantify Impact**: Use the *'Accomplished [X] as measured by [Y], by doing [Z]'* formula for projects and experiences.\n"
                f"3. **Clean Structure**: Use single-column standard sections: *Contact Info, Summary, Technical Skills, Projects, Experience, Education*.\n"
                f"4. **Live Validation**: Upload your updated resume to the **Resume Analyzer** tab to view your 8-factor score breakdown!\n\n"
                f"*💡 Tip: Adding completed projects from your learning roadmap directly addresses your current skill gaps.*"
            )

        # 2. Roadmap / Study / Learning questions
        if any(w in msg_lower for w in ['roadmap', 'study', 'learn', 'plan', 'task', 'schedule']):
            gaps_str = ", ".join(priority_gaps) if priority_gaps else "advanced core competencies"
            roadmap_info = f"Your current roadmap is **{roadmap_title}** ({roadmap_progress}% completed)." if roadmap_title else "You can generate an adaptive roadmap in the **Roadmap** tab."
            return (
                f"### 🗺️ DishaAI Personalized Learning Guide for **{name}**\n\n"
                f"{roadmap_info}\n\n"
                f"**Target Goal**: {target_career_title} (Current Readiness: **{readiness_score}%**)\n\n"
                f"**Immediate Next Focus Areas**:\n"
                + ("\n".join([f"- **Bridge {skill}**: Complete relevant roadmap milestone exercises and build a mini-project." for skill in priority_gaps]) if priority_gaps else "- Continue executing your daily study planner tasks.")
                + "\n\n"
                f"**Recommended Study Schedule**:\n"
                f"- **45 mins**: Theory & concept documentation\n"
                f"- **60 mins**: Hands-on coding or lab exercises\n"
                f"- **15 mins**: Knowledge check quiz to lock in XP\n\n"
                f"Check your **Daily Study Planner** on the dashboard to track today's assigned tasks!"
            )

        # 3. Career / Readiness / Gap questions
        if any(w in msg_lower for w in ['career', 'job', 'match', 'readiness', 'gap']):
            return (
                f"### 🎯 Career Guidance for **{name}**\n\n"
                f"**Target Path**: {target_career_title}\n"
                f"**Calculated Readiness**: **{readiness_score}%**\n\n"
                f"**Verified Strengths**: {', '.join(current_skills) if current_skills else 'Beginner profile'}\n\n"
                f"**Priority Gaps to Close**: {', '.join(priority_gaps) if priority_gaps else 'None pending!'}\n\n"
                f"To increase your readiness score above 80%, focus on completing milestones in your adaptive roadmap and verifying skills via quizzes."
            )

        # 4. General query or greeting
        skills_summary = f"with recognized skills in **{', '.join(current_skills[:4])}**" if current_skills else ""
        return (
            f"Hello **{name}**! 👋 I'm your DishaAI Learning & Career Advisor.\n\n"
            f"You are currently tracking toward **{target_career_title}** with a career readiness score of **{readiness_score}%** {skills_summary}.\n\n"
            f"Here are a few ways I can help you right now:\n"
            f"- **Resume Optimization**: Ask me how to tailor your resume for {target_career_title}.\n"
            f"- **Roadmap Guidance**: Ask *'How should I learn {priority_gaps[0] if priority_gaps else 'my next skill'}?'*\n"
            f"- **Study Tasks**: Check your **Study Planner** tab for today's milestone tasks.\n"
            f"- **Skill Assessment**: Take a quiz to test your proficiency and earn XP!\n\n"
            f"What would you like to work on today?"
        )

    def generate_reply(self, user, session, new_message: str, exclude_message_id=None) -> str:
        """
        High-level entry point:
        1. Validates configuration.
        2. Retrieves student context.
        3. Builds system prompt.
        4. Fetches recent conversation history.
        5. Calls the configured LLM API with timeout & retries.
        6. If LLM is unconfigured or temporarily unavailable, returns an intelligent
           context-aware fallback derived from the student's database profile.
        """
        self.reload_config()

        # If API key is not configured or placeholder, safely provide contextual offline advisory
        if not self.api_key or self.api_key.startswith('your_'):
            logger.info("AI_API_KEY unconfigured or placeholder. Serving intelligent contextual offline fallback.")
            return self._generate_offline_fallback(user, new_message)

        user_id = getattr(user, 'id', 'anonymous')
        session_id = getattr(session, 'id', 'none')
        logger.info(
            "Generating AI reply for user_id=%s session_id=%s provider=%s model=%s",
            user_id, session_id, self.provider, self.model
        )

        student_context = self.get_student_context(user)
        system_prompt = self.build_system_prompt(student_context)
        history = self.get_recent_history(session, exclude_message_id=exclude_message_id, limit=10)

        try:
            if self.provider == 'gemini':
                return self._call_gemini(system_prompt, history, new_message)
            elif self.provider == 'groq':
                base_url = self.base_url or "https://api.groq.com/openai/v1"
                return self._call_openai_compatible(base_url, system_prompt, history, new_message)
            elif self.provider in ('openai', 'custom'):
                base_url = self.base_url or "https://api.openai.com/v1"
                return self._call_openai_compatible(base_url, system_prompt, history, new_message)
            else:
                return self._call_gemini(system_prompt, history, new_message)
        except Exception as exc:
            logger.warning("AI provider call failed (%s). Gracefully falling back to DishaAI contextual response.", exc)
            return self._generate_offline_fallback(user, new_message)


# Global singleton instance
ai_service = AIService()

