import React, { useEffect, useState } from 'react';
import { profileApi } from '../../api';
import { StudentProfile } from '../../types';
import { User, Phone, GraduationCap, Briefcase, FileUp, Save, CheckCircle2, AlertCircle } from 'lucide-react';

export const Profile: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [linkedinFile, setLinkedinFile] = useState<File | null>(null);

  useEffect(() => {
    profileApi.getProfile()
      .then(res => {
        setProfile(res);
        setFormData({
          full_name: res.full_name || '',
          phone: res.phone || '',
          department: res.department || '',
          cgpa: res.cgpa || 0,
          year_of_study: res.year_of_study || 4,
          career_goal: res.career_goal || '',
          github_url: res.github_url || '',
        });
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const updated = await profileApi.updateProfile(formData);
      setProfile(updated);
      setMessage('Profile updated successfully!');
    } catch (err: any) {
      setMessage('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) return;
    try {
      const res = await profileApi.uploadResume(resumeFile);
      setMessage(`Resume uploaded: ${res.resume_file_path}`);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Resume upload failed');
    }
  };

  const handleLinkedinUpload = async () => {
    if (!linkedinFile) return;
    try {
      const res = await profileApi.uploadLinkedin(linkedinFile);
      setMessage(`LinkedIn PDF uploaded: ${res.linkedin_pdf_path}`);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'LinkedIn upload failed');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading student profile...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Student Profile Settings</h2>
          <p className="text-xs text-slate-500">Manage academic details, uploads, and career targets</p>
        </div>
        <div className="text-right">
          <span className="text-xs font-semibold text-slate-400">Completion</span>
          <p className="text-2xl font-bold text-linkedin-blue">{profile?.profile_completion_pct}%</p>
        </div>
      </div>

      {message && (
        <div className="p-4 bg-blue-50 dark:bg-blue-950/40 text-linkedin-blue border border-blue-200 dark:border-blue-800 rounded-xl text-sm flex items-center gap-2">
          <CheckCircle2 size={18} />
          <span>{message}</span>
        </div>
      )}

      {/* Main Profile Form */}
      <form onSubmit={handleSave} className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <User size={18} className="text-linkedin-blue" /> Personal & Academic Credentials
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Full Name</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={e => setFormData({ ...formData, full_name: e.target.value })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Phone Number</label>
            <input
              type="text"
              value={formData.phone}
              onChange={e => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Department</label>
            <input
              type="text"
              value={formData.department}
              onChange={e => setFormData({ ...formData, department: e.target.value })}
              placeholder="Computer Science & Engineering"
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">CGPA (0 - 10)</label>
            <input
              type="number"
              step="0.01"
              value={formData.cgpa}
              onChange={e => setFormData({ ...formData, cgpa: parseFloat(e.target.value) || 0 })}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Career Goal Target</label>
            <input
              type="text"
              value={formData.career_goal}
              onChange={e => setFormData({ ...formData, career_goal: e.target.value })}
              placeholder="e.g. SDE, Data Analyst, Cloud Architect"
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">GitHub Profile URL</label>
            <input
              type="text"
              value={formData.github_url}
              onChange={e => setFormData({ ...formData, github_url: e.target.value })}
              placeholder="https://github.com/username"
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="px-6 py-2.5 bg-linkedin-blue hover:bg-linkedin-hover text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-2 transition-colors"
        >
          <Save size={16} />
          <span>{saving ? 'Saving...' : 'Save Profile Changes'}</span>
        </button>
      </form>

      {/* Uploads Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Resume PDF */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h4 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileUp size={18} className="text-linkedin-blue" /> Upload Resume PDF (Max 10MB)
          </h4>
          <input
            type="file"
            accept="application/pdf"
            onChange={e => setResumeFile(e.target.files?.[0] || null)}
            className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-linkedin-blue hover:file:bg-blue-100"
          />
          <button
            onClick={handleResumeUpload}
            disabled={!resumeFile}
            className="w-full py-2 bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg disabled:opacity-50 transition-colors"
          >
            Upload Resume PDF
          </button>
          {profile?.resume_file_path && (
            <p className="text-xs text-slate-400 truncate">Current: {profile.resume_file_path}</p>
          )}
        </div>

        {/* LinkedIn PDF */}
        <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h4 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileUp size={18} className="text-linkedin-blue" /> Upload LinkedIn PDF (Max 10MB)
          </h4>
          <input
            type="file"
            accept="application/pdf"
            onChange={e => setLinkedinFile(e.target.files?.[0] || null)}
            className="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-linkedin-blue hover:file:bg-blue-100"
          />
          <button
            onClick={handleLinkedinUpload}
            disabled={!linkedinFile}
            className="w-full py-2 bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg disabled:opacity-50 transition-colors"
          >
            Upload LinkedIn PDF
          </button>
          {profile?.linkedin_pdf_path && (
            <p className="text-xs text-slate-400 truncate">Current: {profile.linkedin_pdf_path}</p>
          )}
        </div>
      </div>
    </div>
  );
};
