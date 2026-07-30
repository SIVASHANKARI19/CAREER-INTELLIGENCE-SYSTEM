import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../../api';
import { KeyRound, Mail, CheckCircle2 } from 'lucide-react';

export const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authApi.forgotPassword(email);
      setMessage(res.message);
    } catch (err: any) {
      setMessage('Request processed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F3F2EF] dark:bg-[#1D2226] p-4">
      <div className="w-full max-w-md bg-white dark:bg-[#242B31] p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-lg space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-linkedin-blue rounded-xl flex items-center justify-center text-white font-bold text-xl mx-auto shadow-sm">
            AI
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reset Password</h1>
          <p className="text-xs text-slate-500">Enter your registered email address</p>
        </div>

        {message && (
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 border border-emerald-200 dark:border-emerald-800 rounded-xl text-xs flex items-center gap-2">
            <CheckCircle2 size={16} />
            <span>{message}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="student@example.com"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <KeyRound size={16} />
            <span>{loading ? 'Sending...' : 'Send Reset Link'}</span>
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-800">
          Remember password?{' '}
          <Link to="/login" className="font-semibold text-linkedin-blue hover:underline">
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
