import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, User, FileText, Github, Linkedin, Network,
  Award, Target, Compass, PlayCircle, ShieldCheck, Database,
  Cpu, Building2, BarChart3, LogOut
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';

  const studentLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/profile', label: 'Student Profile', icon: User },
    { to: '/resume', label: 'Resume ATS Analyzer', icon: FileText },
    { to: '/github', label: 'GitHub Code Audit', icon: Github },
    { to: '/linkedin', label: 'LinkedIn Profile PDF', icon: Linkedin },
    { to: '/fusion', label: 'Triangulation Fusion', icon: Network },
    { to: '/readiness', label: '7-Dim Readiness', icon: Award },
    { to: '/skill-gap', label: 'Skill Gap Matrix', icon: Target },
    { to: '/roadmap', label: 'Learning Roadmap', icon: Compass },
    { to: '/simulator', label: 'Career Simulator', icon: PlayCircle },
  ];

  const adminLinks = [
    { to: '/admin', label: 'Admin Dashboard', icon: ShieldCheck },
    { to: '/admin/students', label: 'Student Directory', icon: User },
    { to: '/admin/dataset', label: 'Dataset Management', icon: Database },
    { to: '/admin/model-retrain', label: 'Model Retraining', icon: Cpu },
    { to: '/admin/company-requirements', label: 'Company Requirements', icon: Building2 },
    { to: '/admin/analytics', label: 'Cohort Analytics', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-[#242B31] border-r border-slate-200 dark:border-slate-800 flex flex-col h-screen sticky top-0 z-30 transition-colors">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-linkedin-blue flex items-center justify-center text-white font-bold text-lg shadow-sm">
            AI
          </div>
          <div>
            <h1 className="font-bold text-slate-900 dark:text-white text-base leading-none">PlacementAI</h1>
            <span className="text-[10px] text-linkedin-blue font-semibold tracking-wider uppercase">Intelligence Portal</span>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
            Student Intelligence
          </p>
          <nav className="space-y-1">
            {studentLinks.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-linkedin-blue/10 text-linkedin-blue font-semibold dark:bg-linkedin-blue/20 dark:text-linkedin-accent'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`
                  }
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {isAdmin && (
          <div>
            <p className="px-3 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
              Admin & Model Control
            </p>
            <nav className="space-y-1">
              {adminLinks.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-linkedin-blue/10 text-linkedin-blue font-semibold dark:bg-linkedin-blue/20 dark:text-linkedin-accent'
                          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`
                    }
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
        <div className="flex items-center justify-between p-2">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-bold text-slate-700 dark:text-slate-200 text-sm">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">{user?.email}</p>
              <p className="text-[10px] text-slate-400 capitalize">{user?.role || 'Student'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
