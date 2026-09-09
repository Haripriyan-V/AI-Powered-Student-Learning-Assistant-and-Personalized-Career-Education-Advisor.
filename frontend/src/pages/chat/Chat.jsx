import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  PaperAirplaneIcon,
  ChatBubbleBottomCenterTextIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  XMarkIcon,
  SparklesIcon,
  BriefcaseIcon,
  LightBulbIcon,
  CommandLineIcon,
  DocumentCheckIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const QUICK_PROMPTS = [
  {
    icon: SparklesIcon,
    label: 'Bridge My Skill Gaps',
    prompt: 'Based on my current skill profile and target career goal, what is the best sequence to bridge my biggest skill gaps?',
  },
  {
    icon: LightBulbIcon,
    label: 'Explain a Concept',
    prompt: 'Explain the core principles of Deep Learning and Neural Networks in beginner-friendly terms with an example.',
  },
  {
    icon: CommandLineIcon,
    label: 'Code Practice Problem',
    prompt: 'Generate a practical intermediate Python code exercise for me, complete with problem statement, constraints, and test cases.',
  },
  {
    icon: DocumentCheckIcon,
    label: 'Quick Knowledge Quiz',
    prompt: 'Generate a 3-question multiple-choice quiz on SQL and Database design based on my current skill level.',
  },
  {
    icon: BriefcaseIcon,
    label: 'Interview Prep',
    prompt: 'What are the top 5 technical interview questions asked for my target career role and how should I approach answering them?',
  },
];

function ChatMessage({ msg }) {
  const isUser = msg.sender === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-xl lg:max-w-2xl px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-iris-600 text-white rounded-br-none shadow-sm'
            : 'surface text-ink-900 dark:text-ink-50 rounded-bl-none border border-ink-200 dark:border-ink-800 shadow-2xs'
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none text-ink-900 dark:text-ink-100 leading-relaxed overflow-x-auto">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="my-2 list-disc list-inside space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="my-2 list-decimal list-inside space-y-1">{children}</ol>,
                code: ({ node, inline, className, children, ...props }) => {
                  return inline ? (
                    <code className="px-1.5 py-0.5 rounded bg-ink-100 dark:bg-ink-800 font-mono text-xs text-iris-600 dark:text-iris-400" {...props}>
                      {children}
                    </code>
                  ) : (
                    <pre className="p-3 my-2 rounded-xl bg-ink-900 text-ink-50 font-mono text-xs overflow-x-auto border border-ink-800">
                      <code>{children}</code>
                    </pre>
                  );
                },
              }}
            >
              {msg.message}
            </ReactMarkdown>
          </div>
        )}

        <p className={`text-[10px] mt-1.5 ${isUser ? 'text-iris-200 text-right' : 'text-ink-400'}`}>
          {msg.created_at
            ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : 'Just now'}
        </p>
      </div>
    </motion.div>
  );
}

export default function Chat() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [studentContext, setStudentContext] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  // Load sessions and student context on mount
  useEffect(() => {
    Promise.all([
      api.get('/chatbot/sessions/'),
      api.get('/career/skill-gap/').catch(() => ({ data: null })),
    ])
      .then(async ([sessRes, gapRes]) => {
        const sessionsData = sessRes.data;
        const list = Array.isArray(sessionsData) ? sessionsData : sessionsData.results || [];
        setSessions(list);
        setStudentContext(gapRes.data);

        if (list.length > 0) {
          const firstSession = list[0];
          setActiveSession(firstSession);
          try {
            const detailRes = await api.get(`/chatbot/sessions/${firstSession.id}/`);
            setMessages(detailRes.data.messages || []);
          } catch (fetchErr) {
            setMessages(firstSession.messages || []);
          }
        }
      })
      .catch((err) => console.error('Error loading chat:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectSession = async (session) => {
    if (activeSession?.id === session.id) return;
    setActiveSession(session);
    setError(null);
    try {
      const res = await api.get(`/chatbot/sessions/${session.id}/`);
      setMessages(res.data.messages || []);
    } catch (err) {
      setMessages(session.messages || []);
    }
  };

  const handleNewSession = () => {
    api
      .post('/chatbot/sessions/', { title: `Study Session ${new Date().toLocaleDateString()}` })
      .then((res) => {
        setSessions((prev) => [res.data, ...prev]);
        setActiveSession(res.data);
        setMessages([]);
        setError(null);
      })
      .catch((err) => console.error('Error creating chat session:', err));
  };

  const sendMessageRequest = async (messageText) => {
    if (!messageText.trim() || !activeSession || sending) return;

    setSending(true);
    setError(null);
    const textToSend = messageText.trim();

    try {
      const res = await api.post(`/chatbot/sessions/${activeSession.id}/send_message/`, {
        message: textToSend,
      });

      setMessages((prev) => [
        ...prev,
        res.data.user_message,
        res.data.assistant_message,
      ]);
      setInputText('');
      setError(null);
    } catch (err) {
      console.error('Error sending message:', err);
      if (err.response?.data?.user_message) {
        setMessages((prev) => [...prev, err.response.data.user_message]);
        setInputText('');
      }
      setError({
        message: err.response?.data?.error || 'Unable to connect to AI assistant. Please try again.',
        retryText: textToSend,
      });
    } finally {
      setSending(false);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    sendMessageRequest(inputText);
  };

  const handleQuickPromptClick = (prompt) => {
    if (sending) return;
    sendMessageRequest(prompt);
  };

  if (loading) return <Loader label="Connecting to DishaAI Learning Assistant…" size="lg" />;

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Sidebar - Sessions list */}
      <div className="w-64 hidden lg:flex flex-col border-r border-ink-100 dark:border-ink-800 bg-ink-25 dark:bg-ink-950 rounded-2xl p-4">
        <button onClick={handleNewSession} className="btn-primary w-full mb-4 flex items-center justify-center gap-2">
          <span>+ New Session</span>
        </button>
        <div className="flex-1 overflow-y-auto space-y-1.5">
          {sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => handleSelectSession(session)}
              className={`w-full text-left px-3 py-2 rounded-xl transition-colors text-xs font-medium truncate ${
                activeSession?.id === session.id
                  ? 'bg-iris-600 text-white shadow-xs'
                  : 'text-ink-700 dark:text-ink-300 hover:bg-ink-100 dark:hover:bg-ink-800'
              }`}
            >
              {session.title || `Session #${session.id}`}
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {activeSession ? (
          <>
            {/* Header & Student Context Pill */}
            <div className="mb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h1 className="text-xl font-bold text-ink-900 dark:text-ink-50">
                  {activeSession.title || 'AI Learning Assistant'}
                </h1>
                <p className="text-xs text-ink-500">
                  Personalized 360° Learning, Concept Explanations, Code & Interview Coach
                </p>
              </div>

              {/* Context Pill */}
              {studentContext && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-iris-50 dark:bg-iris-950/40 border border-iris-200 dark:border-iris-800 text-[11px] text-iris-700 dark:text-iris-300 self-start sm:self-auto">
                  <span className="h-2 w-2 rounded-full bg-growth-500 animate-pulse" />
                  <span>
                    Context: <strong>{studentContext.career_path_title || 'Software / AI'}</strong> ({studentContext.readiness_score}% Readiness)
                  </span>
                </div>
              )}
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto mb-3 p-4 lg:p-6 bg-ink-50/60 dark:bg-ink-900/40 rounded-2xl border border-ink-100 dark:border-ink-800/80">
              {messages.length === 0 && !sending ? (
                <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto space-y-4">
                  <div className="h-14 w-14 rounded-2xl bg-iris-500/10 text-iris-600 flex items-center justify-center">
                    <SparklesIcon className="h-7 w-7" />
                  </div>
                  <div>
                    <p className="font-bold text-ink-900 dark:text-ink-50 text-base">
                      How can I help you learn today?
                    </p>
                    <p className="text-xs text-ink-500 mt-1">
                      I understand your verified skills, active roadmap tasks, and biggest skill gaps. Choose a quick action below or ask any question!
                    </p>
                  </div>
                </div>
              ) : (
                messages.map((msg) => (
                  <ChatMessage key={msg.id || `${msg.sender}-${msg.created_at}`} msg={msg} />
                ))
              )}

              {/* In-flight typing indicator */}
              {sending && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start mb-4"
                >
                  <div className="surface px-4 py-3 rounded-2xl rounded-bl-none border border-ink-200 dark:border-ink-800 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-iris-500 animate-bounce" />
                    <span className="w-2 h-2 rounded-full bg-iris-500 animate-bounce [animation-delay:0.2s]" />
                    <span className="w-2 h-2 rounded-full bg-iris-500 animate-bounce [animation-delay:0.4s]" />
                    <span className="text-xs text-ink-500 ml-1">Analyzing your skill profile & formulating reply…</span>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Prompt Suggestion Chips */}
            <div className="mb-3 flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              {QUICK_PROMPTS.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleQuickPromptClick(item.prompt)}
                    disabled={sending}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-white dark:bg-ink-900 border border-ink-200 dark:border-ink-800 hover:border-iris-400 hover:text-iris-600 dark:hover:text-iris-400 text-ink-700 dark:text-ink-300 shrink-0 transition-colors shadow-2xs"
                  >
                    <Icon className="h-3.5 w-3.5 text-iris-500" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Error Banner */}
            {error && (
              <div className="mb-3 px-4 py-2 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 flex-1">
                  <ExclamationCircleIcon className="h-4 w-4 text-red-500 shrink-0" />
                  <span>{error.message}</span>
                </div>
                {error.retryText && (
                  <button
                    onClick={() => sendMessageRequest(error.retryText)}
                    className="underline font-bold text-red-700 dark:text-red-300"
                  >
                    Retry
                  </button>
                )}
              </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Ask about concepts, skill gaps, code challenges, or interview prep…"
                disabled={sending}
                className="flex-1 input text-sm"
              />
              <button
                type="submit"
                disabled={sending || !inputText.trim()}
                className="btn-primary px-5 flex items-center justify-center"
              >
                <PaperAirplaneIcon className="h-4 w-4" />
              </button>
            </form>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <ChatBubbleBottomCenterTextIcon className="h-12 w-12 text-ink-300 dark:text-ink-600" />
            <p className="text-ink-500 text-sm">No chat sessions open</p>
            <button onClick={handleNewSession} className="btn-primary">
              Start a New Learning Session
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
