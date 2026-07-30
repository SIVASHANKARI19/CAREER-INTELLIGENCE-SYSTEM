import React, { useEffect, useState } from 'react';
import { adminApi } from '../../api';
import { CompanyRequirement } from '../../types';
import { Building2, Plus, CheckCircle2 } from 'lucide-react';

export const CompanyRequirements: React.FC = () => {
  const [requirements, setRequirements] = useState<CompanyRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newCompany, setNewCompany] = useState({
    company_name: '',
    role: '',
    required_skills: '',
    min_cgpa: 8.0,
    notes: ''
  });

  const fetchRequirements = () => {
    setLoading(true);
    adminApi.getCompanyRequirements()
      .then(res => setRequirements(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRequirements();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skillsArray = newCompany.required_skills.split(',').map(s => s.trim()).filter(Boolean);
      await adminApi.createCompanyRequirement({
        company_name: newCompany.company_name,
        role: newCompany.role,
        required_skills: skillsArray,
        min_cgpa: newCompany.min_cgpa,
        notes: newCompany.notes
      });
      setShowModal(false);
      fetchRequirements();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-linkedin-blue/10 text-linkedin-blue rounded-xl">
            <Building2 size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Recruiter Company Requirements</h2>
            <p className="text-xs text-slate-500">Configure corporate target benchmarks for skill gap alignment</p>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-linkedin-blue hover:bg-linkedin-hover text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-1 transition-colors"
        >
          <Plus size={16} />
          <span>Add Company Benchmark</span>
        </button>
      </div>

      {/* Grid of Company Requirements */}
      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading recruiter criteria...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {requirements.map((req) => (
            <div key={req.id} className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-white">{req.company_name}</h3>
                  <p className="text-xs text-linkedin-blue font-semibold">{req.role}</p>
                </div>
                <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold">
                  Min CGPA: {req.min_cgpa || 'None'}
                </span>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase">Required Skill Keywords</p>
                <div className="flex flex-wrap gap-1.5">
                  {req.required_skills.map((s, i) => (
                    <span key={i} className="px-2.5 py-1 bg-blue-50 dark:bg-blue-950/50 text-linkedin-blue text-xs font-semibold rounded-md border border-blue-200 dark:border-blue-800">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {req.notes && (
                <p className="text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-800">
                  Notes: {req.notes}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-[#242B31] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xl max-w-md w-full space-y-4">
            <h3 className="font-bold text-lg text-slate-900 dark:text-white">Add Company Requirement</h3>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={newCompany.company_name}
                  onChange={e => setNewCompany({ ...newCompany, company_name: e.target.value })}
                  placeholder="e.g. Microsoft"
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Role Title</label>
                <input
                  type="text"
                  required
                  value={newCompany.role}
                  onChange={e => setNewCompany({ ...newCompany, role: e.target.value })}
                  placeholder="e.g. Cloud Engineer"
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Required Skills (comma separated)</label>
                <input
                  type="text"
                  required
                  value={newCompany.required_skills}
                  onChange={e => setNewCompany({ ...newCompany, required_skills: e.target.value })}
                  placeholder="Python, AWS, Docker, Kubernetes"
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Minimum CGPA</label>
                <input
                  type="number"
                  step="0.1"
                  value={newCompany.min_cgpa}
                  onChange={e => setNewCompany({ ...newCompany, min_cgpa: parseFloat(e.target.value) || 0 })}
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Notes / Instructions</label>
                <textarea
                  value={newCompany.notes}
                  onChange={e => setNewCompany({ ...newCompany, notes: e.target.value })}
                  className="w-full p-2 bg-slate-50 dark:bg-slate-800 border rounded-lg"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 bg-slate-200 rounded-lg">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-linkedin-blue text-white rounded-lg font-semibold">Save Requirement</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
