import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { profilesAPI } from '../api/client';
import { toast } from 'react-toastify';
import { FiUser, FiBriefcase, FiBook, FiPlus, FiEdit2, FiTrash2, FiSave, FiX } from 'react-icons/fi';
import { Accordion } from 'react-bootstrap';

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState({
    skills: false,
    education: false,
    experience: false,
    projects: false
  });

  const [newSkill, setNewSkill] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [newItem, setNewItem] = useState({
    education: { institution: '', degree: '', field: '', startDate: '', endDate: '', gpa: '' },
    experience: { company: '', position: '', location: '', startDate: '', endDate: '', description: '' },
    projects: { name: '', description: '', technologies: '', link: '', startDate: '', endDate: '' }
  });

  // accordian state for experience section
  const [openExpIndex, setOpenExpIndex] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await profilesAPI.getLatest(); // this is the Axios response
      console.log("data fetched for profile is : ", res);
      setProfile(res.data); // store just the profile object
    } catch (error) {
      if (error.response?.status === 404) {
        toast.info('No profile found. Upload a resume to create one!');
      } else {
        toast.error('Failed to load profile');
      }
    } finally {
      setLoading(false);
    }
};


  const handleAddSkill = async () => {
    if (!newSkill.trim()) return;
    
    try {
      const updatedSkills = [...(profile.skills || []), newSkill.trim()];
      const updated = await profilesAPI.update(profile.id, { skills: updatedSkills });
      setProfile(updated);
      setNewSkill('');
      toast.success('Skill added successfully');
    } catch (error) {
      toast.error('Failed to add skill');
    }
  };

  const handleRemoveSkill = async (index) => {
    try {
      const updatedSkills = profile.skills.filter((_, i) => i !== index);
      const updated = await profilesAPI.update(profile.id, { skills: updatedSkills });
      setProfile(updated);
      toast.success('Skill removed successfully');
    } catch (error) {
      toast.error('Failed to remove skill');
    }
  };

  const handleAddItem = async (type) => {
    const item = newItem[type];
    
    // Validate required fields
    if (type === 'education' && (!item.institution || !item.degree)) {
      toast.error('Institution and degree are required');
      return;
    }
    if (type === 'experience' && (!item.company || !item.position)) {
      toast.error('Company and position are required');
      return;
    }
    if (type === 'projects' && !item.name) {
      toast.error('Project name is required');
      return;
    }

    try {
      const updatedItems = [...(profile[type] || []), item];
      const updated = await profilesAPI.update(profile.id, { [type]: updatedItems });
      setProfile(updated);
      
      // Reset form
      setNewItem(prev => ({
        ...prev,
        [type]: type === 'education' 
          ? { institution: '', degree: '', field: '', startDate: '', endDate: '', gpa: '' }
          : type === 'experience'
          ? { company: '', position: '', location: '', startDate: '', endDate: '', description: '' }
          : { name: '', description: '', technologies: '', link: '', startDate: '', endDate: '' }
      }));
      
      setEditMode(prev => ({ ...prev, [type]: false }));
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1, -1)} added successfully`);
    } catch (error) {
      toast.error(`Failed to add ${type.slice(0, -1)}`);
    }
  };

  const handleUpdateItem = async (type, index, updatedItem) => {
    try {
      const updatedItems = [...profile[type]];
      updatedItems[index] = updatedItem;
      const updated = await profilesAPI.update(profile.id, { [type]: updatedItems });
      setProfile(updated);
      setEditingItem(null);
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1, -1)} updated successfully`);
    } catch (error) {
      toast.error(`Failed to update ${type.slice(0, -1)}`);
    }
  };

  const handleRemoveItem = async (type, index) => {
    try {
      const updatedItems = profile[type].filter((_, i) => i !== index);
      const updated = await profilesAPI.update(profile.id, { [type]: updatedItems });
      setProfile(updated);
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1, -1)} removed successfully`);
    } catch (error) {
      toast.error(`Failed to remove ${type.slice(0, -1)}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <FiUser className="mx-auto h-16 w-16 text-gray-400 mb-4" />
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">No Profile Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">Upload a resume to create your profile</p>
        <a
          href="/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          Upload Resume
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile</h1>
      </div>

      {/* Basic Information */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center mb-4">
          <FiUser className="h-6 w-6 text-primary-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Basic Information</h2>
        </div>
        <div className="space-y-2">
          <p className="text-gray-700 dark:text-gray-300">
            <span className="font-medium">Email:</span> {user?.email}
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            <span className="font-medium">Name:</span> {user?.full_name || 'Not provided'}
          </p>
          <p className="text-gray-700 dark:text-gray-300">
            <span className="font-medium">Profile Created:</span> {profile && new Date(profile.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Skills Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <FiBook className="h-6 w-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Skills</h2>
          </div>
          <button
            onClick={() => setEditMode(prev => ({ ...prev, skills: !prev.skills }))}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            {editMode.skills ? <FiX className="h-5 w-5" /> : <FiPlus className="h-5 w-5" />}
          </button>
        </div>

        {editMode.skills && (
          <div className="mb-4 flex gap-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              placeholder="Add a skill..."
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <button
              onClick={handleAddSkill}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <FiPlus className="h-5 w-5" />
            </button>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {profile.skills?.length > 0 ? (
            profile.skills.map((skill, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
              >
                {skill}
                {editMode.skills && (
                  <button
                    onClick={() => handleRemoveSkill(index)}
                    className="ml-2 text-primary-600 hover:text-primary-800 dark:text-primary-400"
                  >
                    <FiX className="h-4 w-4" />
                  </button>
                )}
              </span>
            ))
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No skills added yet</p>
          )}
        </div>
      </div>

      {/* Experience Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <FiBriefcase className="h-6 w-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Experience</h2>
          </div>
          {/* button to add new experience */}
          <button
            onClick={() => setEditMode(prev => ({ ...prev, experience: !prev.experience }))}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            {editMode.experience ? <FiX className="h-5 w-5" /> : <FiPlus className="h-5 w-5" />}
          </button>
        </div>


        {/* this is for adding new experience - the fields */}
        {editMode.experience && (
          <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
            <input
              type="text"
              placeholder="Company"
              value={newItem.experience.company}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                experience: { ...prev.experience, company: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Position"
              value={newItem.experience.position}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                experience: { ...prev.experience, position: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Location"
              value={newItem.experience.location}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                experience: { ...prev.experience, location: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="Start Date (e.g., Jan 2020)"
                value={newItem.experience.startDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  experience: { ...prev.experience, startDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="text"
                placeholder="End Date (e.g., Present)"
                value={newItem.experience.endDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  experience: { ...prev.experience, endDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <textarea
              placeholder="Description"
              value={newItem.experience.description}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                experience: { ...prev.experience, description: e.target.value }
              }))}
              rows="3"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <button
              onClick={() => handleAddItem('experience')}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Add Experience
            </button>
          </div>
        )}

        {/* display all the experiences */}
        <div className="space-y-4">
          {profile.experience?.length > 0 ? (
              profile.experience.map((exp, index) => {
                const isOpen = openExpIndex === index;
                const headerLabel = `${exp.position} • ${exp.company} • ${exp.start_date || exp.startDate || ''} - ${exp.end_date || exp.endDate || exp.end_date || ''}`;

                return (
                  <div key={index} className="border-l-4 border-primary-500 pl-4 py-2">
                    <button
                      type="button"
                      onClick={() => setOpenExpIndex(isOpen ? null : index)}
                      aria-expanded={isOpen}
                      className="w-full flex justify-between items-center text-left focus:outline-none"
                    >
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{exp.position}</h3>
                        <p className="text-primary-600 dark:text-primary-400">{exp.company}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {exp.start_date || exp.startDate || ''} {exp.end_date || exp.endDate || '' ? ` - ${exp.end_date || exp.endDate || exp.end_date}` : ''}
                        </p>
                      </div>

                      <div className="ml-4 flex items-center gap-3">
                        {(exp.location) && <span className="text-sm text-gray-600 dark:text-gray-400">{exp.location}</span>}
                        <svg
                          className={`h-5 w-5 transform transition-transform duration-200 ${isOpen ? 'rotate-180' : 'rotate-0'}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                      </div>
                    </button>

                    {isOpen && (
                      <div className="mt-3 pl-2 text-gray-700 dark:text-gray-300">
                        {exp.responsibilities && exp.responsibilities.length > 0 ? (
                          <ul className="list-disc pl-5 space-y-2">
                            {exp.responsibilities.map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        ) : exp.description ? (
                          <p className="whitespace-pre-wrap">{exp.description}</p>
                        ) : (
                          <p className="text-sm text-gray-500 dark:text-gray-400">No details provided.</p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <p className="text-gray-500 dark:text-gray-400">No experience added yet</p>
            )}
        </div>
      </div>

      {/* Education Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <FiBook className="h-6 w-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Education</h2>
          </div>
          <button
            onClick={() => setEditMode(prev => ({ ...prev, education: !prev.education }))}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            {editMode.education ? <FiX className="h-5 w-5" /> : <FiPlus className="h-5 w-5" />}
          </button>
        </div>

        {editMode.education && (
          <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
            <input
              type="text"
              placeholder="Institution"
              value={newItem.education.institution}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                education: { ...prev.education, institution: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Degree"
              value={newItem.education.degree}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                education: { ...prev.education, degree: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Field of Study"
              value={newItem.education.field}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                education: { ...prev.education, field: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <div className="grid grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Start Year"
                value={newItem.education.startDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  education: { ...prev.education, startDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="text"
                placeholder="End Year"
                value={newItem.education.endDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  education: { ...prev.education, endDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="text"
                placeholder="GPA"
                value={newItem.education.gpa}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  education: { ...prev.education, gpa: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <button
              onClick={() => handleAddItem('education')}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Add Education
            </button>
          </div>
        )}

        <div className="space-y-4">
          {profile.education?.length > 0 ? (
            profile.education.map((edu, index) => (
              <div key={index} className="border-l-4 border-primary-500 pl-4 py-2">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{edu.degree}</h3>
                    <p className="text-primary-600 dark:text-primary-400">{edu.institution}</p>
                    {edu.field && <p className="text-gray-700 dark:text-gray-300">{edu.field}</p>}
                    <div className="flex items-center gap-4 mt-1">
                      {(edu.startDate || edu.endDate) && (
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          {edu.startDate} - {edu.endDate}
                        </p>
                      )}
                      {edu.gpa && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">GPA: {edu.gpa}</p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveItem('education', index)}
                    className="text-red-600 hover:text-red-800 dark:text-red-400"
                  >
                    <FiTrash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No education added yet</p>
          )}
        </div>
      </div>

      {/* Projects Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <FiBook className="h-6 w-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Projects</h2>
          </div>
          <button
            onClick={() => setEditMode(prev => ({ ...prev, projects: !prev.projects }))}
            className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            {editMode.projects ? <FiX className="h-5 w-5" /> : <FiPlus className="h-5 w-5" />}
          </button>
        </div>

        {editMode.projects && (
          <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
            <input
              type="text"
              placeholder="Project Name"
              value={newItem.projects.name}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                projects: { ...prev.projects, name: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <textarea
              placeholder="Description"
              value={newItem.projects.description}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                projects: { ...prev.projects, description: e.target.value }
              }))}
              rows="3"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Technologies (e.g., React, Node.js, PostgreSQL)"
              value={newItem.projects.technologies}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                projects: { ...prev.projects, technologies: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <input
              type="text"
              placeholder="Project Link (optional)"
              value={newItem.projects.link}
              onChange={(e) => setNewItem(prev => ({
                ...prev,
                projects: { ...prev.projects, link: e.target.value }
              }))}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
            />
            <div className="grid grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="Start Date"
                value={newItem.projects.startDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  projects: { ...prev.projects, startDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="text"
                placeholder="End Date"
                value={newItem.projects.endDate}
                onChange={(e) => setNewItem(prev => ({
                  ...prev,
                  projects: { ...prev.projects, endDate: e.target.value }
                }))}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <button
              onClick={() => handleAddItem('projects')}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Add Project
            </button>
          </div>
        )}

        <div className="space-y-4">
          {profile.projects?.length > 0 ? (
            profile.projects.map((project, index) => (
              <div key={index} className="border-l-4 border-primary-500 pl-4 py-2">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{project.name}</h3>
                    {(project.startDate || project.endDate) && (
                      <p className="text-sm text-gray-500 dark:text-gray-500">
                        {project.startDate} - {project.endDate}
                      </p>
                    )}
                    {project.description && (
                      <p className="mt-2 text-gray-700 dark:text-gray-300">{project.description}</p>
                    )}
                    {project.technologies && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-medium">Technologies:</span> {project.technologies}
                      </p>
                    )}
                    {project.link && (
                      <a
                        href={project.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-1 inline-block text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
                      >
                        View Project →
                      </a>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveItem('projects', index)}
                    className="text-red-600 hover:text-red-800 dark:text-red-400"
                  >
                    <FiTrash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No projects added yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
