import React, { useEffect, useState } from 'react';
import { profileApi } from '../../api';
import { StudentProfile } from '../../types';
import { User, Phone, GraduationCap, Briefcase, FileUp, Save, CheckCircle2, Plus, Trash2, Award, Code2 } from 'lucide-react';

const inputClass = "w-full px-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-linkedin-blue focus:outline-none";
const labelClass = "block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1";
const sectionClass = "bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4";

interface ProjectItem { title: string; description: string; tech_stack: string[]; link?: string; }
interface CertItem { name: string; issuer: string; date?: string; link?: string; }
interface InternshipItem { company: string; role: string; duration?: string; description?: string; }

export const Profile: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [formData, setFormData] = useState<any>({});
  const [languages, setLanguages] = useState<string[]>([]);
  const [langInput, setLangInput] = useState('');
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [certifications, setCertifications] = useState<CertItem[]>([]);
  const [internships, setInternships] = useState<InternshipItem[]>([]);
  const [achievements, setAchievements] = useState<string[]>([]);
  const [achievementInput, setAchievementInput] = useState('');
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
          year_of_study: res.year_of_study || 1,
          career_goal: res.career_goal || '',
          github_url: res.github_url || '',
        });
        setLanguages(res.programming_languages || []);
        setProjects((res.projects as ProjectItem[]) || []);
        setCertifications((res.certifications as CertItem[]) || []);
        setInternships((res.internships as InternshipItem[]) || []);
        setAchievements(res.achievements || []);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const updated = await profileApi.updateProfile({
        ...formData,
        programming_languages: languages,
        projects,
        certifications,
        internships,
        achievements,
      });
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

  const addLanguage = () => {
    const v = langInput.trim();
    if (v && !languages.includes(v)) setLanguages([...languages, v]);
    setLangInput('');
  };
  const removeLanguage = (lang: string) => setLanguages(languages.filter(l => l !== lang));

  const addAchievement = () => {
    const v = achievementInput.trim();
    if (v) setAchievements([...achievements, v]);
    setAchievementInput('');
  };
  const removeAchievement = (idx: number) => setAchievements(achievements.filter((_, i) => i !== idx));

  const addProject = () => setProjects([...projects, { title: '', description: '', tech_stack: [], link: '' }]);
  const updateProject = (idx: number, field: keyof ProjectItem, value: any) => {
    const next = [...projects];
    (next[idx] as any)[field] = field === 'tech_stack' ? String(value).split(',').map((s: string) => s.trim()).filter(Boolean) : value;
    setProjects(next);
  };
  const removeProject = (idx: number) => setProjects(projects.filter((_, i) => i !== idx));

  const addCertification = () => setCertifications([...certifications, { name: '', issuer: '', date: '', link: '' }]);
  const updateCertification = (idx: number, field: keyof CertItem, value: string) => {
    const next = [...certifications];
    (next[idx] as any)[field] = value;
    setCertifications(next);
  };
  const removeCertification = (idx: number) => setCertifications(certifications.filter((_, i) => i !== idx));

  const addInternship = () => setInternships([...internships, { company: '', role: '', duration: '', description: '' }]);
  const updateInternship = (idx: number, field: keyof InternshipItem, value: string) => {
    const next = [...internships];
    (next[idx] as any)[field] = value;
    setInternships(next);
  };
  const removeInternship = (idx: number) => setInternships(internships.filter((_, i) => i !== idx));

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading student profile...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Student Profile Settings</h2>
          <p className="text-xs text-slate-500">Manage academic details, skills, projects, and career targets</p>
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

      <form onSubmit={handleSave} className="space-y-8">
        <div className={sectionClass}>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <User size={18} className="text-linkedin-blue" /> Personal & Academic Credentials
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className={labelClass}>Full Name</label>
              <input type="text" value={formData.full_name} onChange={e => setFormData({ ...formData, full_name: e.target.value })} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Phone Number</label>
              <input type="text" value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Department</label>
              <input type="text" value={formData.department} onChange={e => setFormData({ ...formData, department: e.target.value })} placeholder="Computer Science & Engineering" className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>CGPA (0 - 10)</label>
              <input type="number" step="0.01" value={formData.cgpa} onChange={e => setFormData({ ...formData, cgpa: parseFloat(e.target.value) || 0 })} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Year of Study</label>
              <select value={formData.year_of_study} onChange={e => setFormData({ ...formData, year_of_study: parseInt(e.target.value) })} className={inputClass}>
                <option value={1}>1st Year</option>
                <option value={2}>2nd Year</option>
                <option value={3}>3rd Year</option>
                <option value={4}>4th Year</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Career Goal Target</label>
              <input type="text" value={formData.career_goal} onChange={e => setFormData({ ...formData, career_goal: e.target.value })} placeholder="e.g. SDE, Data Analyst, Cloud Architect" className={inputClass} />
            </div>
            <div className="md:col-span-2">
              <label className={labelClass}>GitHub Profile URL</label>
              <input type="text" value={formData.github_url} onChange={e => setFormData({ ...formData, github_url: e.target.value })} placeholder="https://github.com/username" className={inputClass} />
            </div>
          </div>
        </div>

        <div className={sectionClass}>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Code2 size={18} className="text-linkedin-blue" /> Programming Languages
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={langInput}
              onChange={e => setLangInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addLanguage(); } }}
              placeholder="e.g. Python — press Enter to add"
              className={inputClass}
            />
            <button type="button" onClick={addLanguage} className="px-4 py-2 bg-linkedin-blue text-white rounded-lg text-sm font-semibold shrink-0">Add</button>
          </div>
          <div className="flex flex-wrap gap-2">
            {languages.map(lang => (
              <span key={lang} className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 dark:bg-blue-950/40 text-linkedin-blue rounded-full text-xs font-semibold">
                {lang}
                <button type="button" onClick={() => removeLanguage(lang)} className="hover:text-red-600"><Trash2 size={12} /></button>
              </span>
            ))}
            {languages.length === 0 && <p className="text-xs text-slate-400">No languages added yet.</p>}
          </div>
        </div>

        <div className={sectionClass}>
          <div className="flex justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Briefcase size={18} className="text-linkedin-blue" /> Projects
            </h3>
            <button type="button" onClick={addProject} className="flex items-center gap-1 text-xs font-semibold text-linkedin-blue hover:underline">
              <Plus size={14} /> Add Project
            </button>
          </div>
          {projects.length === 0 && <p className="text-xs text-slate-400">No projects added yet.</p>}
          {projects.map((p, idx) => (
            <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl space-y-3 relative">
              <button type="button" onClick={() => removeProject(idx)} className="absolute top-3 right-3 text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" placeholder="Project title" value={p.title} onChange={e => updateProject(idx, 'title', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Tech stack (comma separated)" value={p.tech_stack?.join(', ') || ''} onChange={e => updateProject(idx, 'tech_stack', e.target.value)} className={inputClass} />
              </div>
              <textarea placeholder="Description" value={p.description} onChange={e => updateProject(idx, 'description', e.target.value)} className={inputClass} rows={2} />
              <input type="text" placeholder="Project link (optional)" value={p.link || ''} onChange={e => updateProject(idx, 'link', e.target.value)} className={inputClass} />
            </div>
          ))}
        </div>

        <div className={sectionClass}>
          <div className="flex justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Award size={18} className="text-linkedin-blue" /> Certifications
            </h3>
            <button type="button" onClick={addCertification} className="flex items-center gap-1 text-xs font-semibold text-linkedin-blue hover:underline">
              <Plus size={14} /> Add Certification
            </button>
          </div>
          {certifications.length === 0 && <p className="text-xs text-slate-400">No certifications added yet.</p>}
          {certifications.map((c, idx) => (
            <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl space-y-3 relative">
              <button type="button" onClick={() => removeCertification(idx)} className="absolute top-3 right-3 text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" placeholder="Certification name" value={c.name} onChange={e => updateCertification(idx, 'name', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Issuer (e.g. AWS, Coursera)" value={c.issuer} onChange={e => updateCertification(idx, 'issuer', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Date (e.g. 2025-06)" value={c.date || ''} onChange={e => updateCertification(idx, 'date', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Certificate link (optional)" value={c.link || ''} onChange={e => updateCertification(idx, 'link', e.target.value)} className={inputClass} />
              </div>
            </div>
          ))}
        </div>

        <div className={sectionClass}>
          <div className="flex justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <GraduationCap size={18} className="text-linkedin-blue" /> Internships
            </h3>
            <button type="button" onClick={addInternship} className="flex items-center gap-1 text-xs font-semibold text-linkedin-blue hover:underline">
              <Plus size={14} /> Add Internship
            </button>
          </div>
          {internships.length === 0 && <p className="text-xs text-slate-400">No internships added yet.</p>}
          {internships.map((i, idx) => (
            <div key={idx} className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl space-y-3 relative">
              <button type="button" onClick={() => removeInternship(idx)} className="absolute top-3 right-3 text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input type="text" placeholder="Company" value={i.company} onChange={e => updateInternship(idx, 'company', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Role" value={i.role} onChange={e => updateInternship(idx, 'role', e.target.value)} className={inputClass} />
                <input type="text" placeholder="Duration (e.g. 3 months)" value={i.duration || ''} onChange={e => updateInternship(idx, 'duration', e.target.value)} className={inputClass} />
              </div>
              <textarea placeholder="Description" value={i.description || ''} onChange={e => updateInternship(idx, 'description', e.target.value)} className={inputClass} rows={2} />
            </div>
          ))}
        </div>

        <div className={sectionClass}>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Award size={18} className="text-linkedin-blue" /> Achievements
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={achievementInput}
              onChange={e => setAchievementInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addAchievement(); } }}
              placeholder="e.g. Winner, Smart India Hackathon 2025 — press Enter to add"
              className={inputClass}
            />
            <button type="button" onClick={addAchievement} className="px-4 py-2 bg-linkedin-blue text-white rounded-lg text-sm font-semibold shrink-0">Add</button>
          </div>
          <ul className="space-y-2">
            {achievements.map((a, idx) => (
              <li key={idx} className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg text-xs">
                <span>{a}</span>
                <button type="button" onClick={() => removeAchievement(idx)} className="text-slate-400 hover:text-red-600"><Trash2 size={14} /></button>
              </li>
            ))}
            {achievements.length === 0 && <p className="text-xs text-slate-400">No achievements added yet.</p>}
          </ul>
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={sectionClass}>
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

        <div className={sectionClass}>
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