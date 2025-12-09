import { useTheme } from '../context/ThemeContext';
import { FiSun, FiMoon, FiType, FiSettings } from 'react-icons/fi';

const Settings = () => {
  const { theme, toggleTheme, fontSize, changeFontSize } = useTheme();

  const fontSizes = [
    { value: 'small', label: 'Small', size: '14px' },
    { value: 'medium', label: 'Medium', size: '16px' },
    { value: 'large', label: 'Large', size: '18px' },
    { value: 'extra-large', label: 'Extra Large', size: '20px' }
  ];

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center mb-6">
        <FiSettings className="h-8 w-8 text-primary-600 mr-3" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
      </div>

      {/* Theme Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">Theme</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Choose between light and dark mode
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {theme === 'light' ? (
              <FiSun className="h-6 w-6 text-yellow-500" />
            ) : (
              <FiMoon className="h-6 w-6 text-blue-400" />
            )}
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={toggleTheme}
            className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors ${
              theme === 'light'
                ? 'border-primary-600 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
            }`}
          >
            <div className="flex items-center justify-center">
              <FiSun className="h-5 w-5 mr-2" />
              <span className="font-medium">Light</span>
            </div>
          </button>

          <button
            onClick={toggleTheme}
            className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors ${
              theme === 'dark'
                ? 'border-primary-600 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
            }`}
          >
            <div className="flex items-center justify-center">
              <FiMoon className="h-5 w-5 mr-2" />
              <span className="font-medium">Dark</span>
            </div>
          </button>
        </div>

        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Current theme: <span className="font-semibold">{theme === 'light' ? 'Light Mode' : 'Dark Mode'}</span>
          </p>
        </div>
      </div>

      {/* Font Size Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">Font Size</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Adjust the text size across the application
            </p>
          </div>
          <FiType className="h-6 w-6 text-primary-600" />
        </div>

        <div className="space-y-3">
          {fontSizes.map((size) => (
            <button
              key={size.value}
              onClick={() => changeFontSize(size.value)}
              className={`w-full py-3 px-4 rounded-lg border-2 text-left transition-colors ${
                fontSize === size.value
                  ? 'border-primary-600 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-primary-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{size.label}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{size.size}</p>
                </div>
                {fontSize === size.value && (
                  <div className="h-3 w-3 rounded-full bg-primary-600"></div>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Current font size: <span className="font-semibold">{fontSizes.find(s => s.value === fontSize)?.label}</span>
          </p>
          <p className="mt-2 text-gray-700 dark:text-gray-300" style={{ fontSize: fontSizes.find(s => s.value === fontSize)?.size }}>
            This is a preview of the selected font size.
          </p>
        </div>
      </div>

      {/* About Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">About ScholarSense</h2>
        <div className="space-y-2 text-gray-700 dark:text-gray-300">
          <p>
            <span className="font-medium">Version:</span> 1.0.0
          </p>
          <p>
            <span className="font-medium">Built with:</span> React, FastAPI, PostgreSQL
          </p>
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            ScholarSense is an AI-powered application assistant that helps you manage opportunities,
            analyze fit scores, and generate tailored materials for academic and professional opportunities.
          </p>
        </div>
      </div>

      {/* Preferences Info */}
      <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-4">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          💡 <span className="font-medium">Tip:</span> Your preferences are saved automatically and will persist across sessions.
        </p>
      </div>
    </div>
  );
};

export default Settings;
