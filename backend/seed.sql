-- ScholarSense Seed Data
-- Sample data for development and testing

-- Insert sample user (password is 'testpassword123' hashed with bcrypt)
INSERT INTO users (email, hashed_password, full_name) VALUES
('john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBq7q3qK4G', 'John Doe'),
('jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBq7q3qK4G', 'Jane Smith');

-- Insert sample documents
INSERT INTO documents (user_id, filename, file_path, file_size, doc_type) VALUES
(1, 'john_resume.pdf', 'storage/uploads/john_resume.pdf', 245678, 'resume'),
(2, 'jane_cv.pdf', 'storage/uploads/jane_cv.pdf', 312456, 'cv');

-- Insert sample document texts
INSERT INTO document_texts (document_id, extracted_text, extraction_method) VALUES
(1, 'JOHN DOE
Software Engineer
Email: john.doe@example.com | Phone: (555) 123-4567

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2020-2024
GPA: 3.8/4.0

SKILLS
Programming: Python, JavaScript, TypeScript, Java, C++
Web: React, Node.js, FastAPI, Django, HTML/CSS
Database: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes
Tools: Git, CI/CD, Agile

EXPERIENCE
Software Engineering Intern - Tech Corp (Summer 2023)
- Built RESTful APIs using FastAPI and PostgreSQL
- Developed React frontend components
- Implemented automated testing with pytest

Research Assistant - University Lab (2022-2024)
- Conducted machine learning research
- Published 2 papers in conferences
- Mentored junior students

PROJECTS
E-commerce Platform
- Full-stack web application with React and Node.js
- Integrated payment processing and authentication
- Deployed on AWS with CI/CD pipeline

AI Chatbot
- NLP-based chatbot using Python and transformers
- Achieved 92% accuracy on test dataset', 'pypdf2'),

(2, 'JANE SMITH
Data Scientist & ML Engineer
jane.smith@example.com

EDUCATION
Master of Science in Data Science - MIT, 2023-2025 (Expected)
Bachelor of Science in Mathematics - Stanford University, 2019-2023

TECHNICAL SKILLS
Languages: Python, R, SQL, Scala
ML/AI: TensorFlow, PyTorch, Scikit-learn, Keras
Data: Pandas, NumPy, Spark, Hadoop
Visualization: Tableau, Matplotlib, Plotly
Cloud: GCP, AWS, Azure ML

PROFESSIONAL EXPERIENCE
Data Science Intern - Google (Summer 2024)
- Developed recommendation algorithms serving 10M+ users
- Improved model accuracy by 15% using ensemble methods
- Collaborated with cross-functional teams

ML Research Assistant - Stanford AI Lab (2021-2023)
- Published 3 papers in top-tier conferences (NeurIPS, ICML)
- Developed novel deep learning architectures
- Mentored 5 undergraduate researchers

PROJECTS
Medical Image Classification
- CNN-based diagnostic tool achieving 95% accuracy
- Deployed as web service using Flask and Docker

Financial Forecasting Model
- LSTM model for stock price prediction
- Backtesting framework with 23% return improvement', 'pypdf2');

-- Insert sample profiles
INSERT INTO profiles (user_id, document_id, full_text, skills, education, experience, projects) VALUES
(1, 1, 'Software Engineer with strong background in full-stack development and machine learning', 
'["Python", "JavaScript", "TypeScript", "React", "FastAPI", "PostgreSQL", "AWS", "Docker"]'::jsonb,
'[{"degree": "Bachelor of Science in Computer Science", "institution": "University of Technology", "year": "2020-2024", "gpa": "3.8/4.0"}]'::jsonb,
'[{"title": "Software Engineering Intern", "company": "Tech Corp", "period": "Summer 2023", "description": "Built RESTful APIs and React components"}, {"title": "Research Assistant", "company": "University Lab", "period": "2022-2024", "description": "ML research and paper publications"}]'::jsonb,
'[{"name": "E-commerce Platform", "description": "Full-stack web app with React and Node.js", "technologies": ["React", "Node.js", "AWS"]}, {"name": "AI Chatbot", "description": "NLP chatbot with 92% accuracy", "technologies": ["Python", "Transformers"]}]'::jsonb),

(2, 2, 'Data Scientist and ML Engineer with expertise in deep learning and production ML systems',
'["Python", "R", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "SQL", "GCP", "AWS"]'::jsonb,
'[{"degree": "Master of Science in Data Science", "institution": "MIT", "year": "2023-2025"}, {"degree": "Bachelor of Science in Mathematics", "institution": "Stanford University", "year": "2019-2023"}]'::jsonb,
'[{"title": "Data Science Intern", "company": "Google", "period": "Summer 2024", "description": "Recommendation algorithms for 10M+ users"}, {"title": "ML Research Assistant", "company": "Stanford AI Lab", "period": "2021-2023", "description": "Published 3 papers in top conferences"}]'::jsonb,
'[{"name": "Medical Image Classification", "description": "CNN diagnostic tool with 95% accuracy", "technologies": ["TensorFlow", "Flask", "Docker"]}, {"name": "Financial Forecasting", "description": "LSTM model for stock prediction", "technologies": ["PyTorch", "Python"]}]'::jsonb);

-- Insert sample opportunities
INSERT INTO opportunities (user_id, title, organization, url, description, fit_score, fit_analysis, status, deadline) VALUES
(1, 'Software Engineering Intern', 'Meta', 'https://www.metacareers.com/jobs', 
'Meta is seeking talented software engineering interns to join our team. You will work on cutting-edge products used by billions of people worldwide.

Requirements:
- Currently pursuing BS/MS in Computer Science or related field
- Strong programming skills in Python, C++, or Java
- Experience with web development (React preferred)
- Understanding of algorithms and data structures
- Passion for building user-facing products

Preferred:
- Previous internship experience
- Open source contributions
- Hackathon participation',
85,
'{"overall_fit": 85, "strengths": ["Strong React and Python experience", "Full-stack development background", "Relevant internship experience at Tech Corp"], "gaps": ["Could highlight more algorithm competition experience", "Limited C++ experience mentioned"], "recommendations": ["Emphasize the e-commerce platform project", "Highlight the scalability of previous work"]}'::jsonb,
'TO_APPLY',
'2025-02-15'),

(1, 'ML Engineer Internship', 'OpenAI', 'https://openai.com/careers',
'Join OpenAI to work on cutting-edge AI research and products. Help us build safe and beneficial AGI.

Requirements:
- Pursuing MS/PhD in CS, ML, or related field
- Strong Python programming
- Deep learning experience (PyTorch/TensorFlow)
- Published research (preferred)
- Excellent mathematical foundation',
72,
'{"overall_fit": 72, "strengths": ["Python expertise", "ML research experience", "AI chatbot project demonstrates NLP knowledge"], "gaps": ["BS level while MS/PhD preferred", "Only 2 publications vs typical 3+ for competitive candidates"], "recommendations": ["Highlight research assistant role prominently", "Emphasize quick learning ability and passion for AI"]}'::jsonb,
'TO_APPLY',
'2025-01-30'),

(2, 'Data Science Internship', 'Netflix', 'https://jobs.netflix.com',
'Netflix is looking for a data science intern to work on personalization and recommendation systems.

Requirements:
- MS in Data Science, Statistics, CS, or related field
- Strong Python and SQL skills
- Experience with ML frameworks (TensorFlow, PyTorch, Scikit-learn)
- Statistical analysis and A/B testing knowledge
- Experience with large-scale data processing

Nice to have:
- Recommendation systems experience
- Production ML deployment
- Cloud platform experience (AWS/GCP)',
92,
'{"overall_fit": 92, "strengths": ["Perfect educational background (MS from MIT)", "Direct experience with recommendation algorithms at Google", "Strong ML framework expertise", "Production ML experience"], "gaps": ["Could mention more about A/B testing experience"], "recommendations": ["Lead with Google recommendation system work", "Emphasize the 10M+ user scale impact", "Highlight cross-functional collaboration skills"]}'::jsonb,
'APPLIED',
'2025-02-28'),

(2, 'AI Research Intern', 'DeepMind', 'https://www.deepmind.com/careers',
'DeepMind seeks exceptional AI researchers to push the boundaries of artificial intelligence.

Requirements:
- PhD student or recent graduate in ML/AI
- Strong publication record in top venues (NeurIPS, ICML, ICLR)
- Expertise in deep learning
- Strong mathematical foundations
- Novel research contributions',
88,
'{"overall_fit": 88, "strengths": ["Excellent publication record (3 papers in NeurIPS, ICML)", "Strong theoretical background from Stanford Math degree", "Novel architecture development experience", "Research mentorship experience"], "gaps": ["PhD student/recent grad preferred, currently MS student", "Could emphasize more theoretical contributions"], "recommendations": ["Highlight the novel architectures work", "Emphasize mathematical foundations from undergrad", "Mention research independence and leadership"]}'::jsonb,
'INTERVIEW',
'2025-03-15');

-- Insert sample opportunity requirements
INSERT INTO opportunity_requirements (opportunity_id, requirement_text, requirement_type, is_mandatory) VALUES
(1, 'Currently pursuing BS/MS in Computer Science or related field', 'education', true),
(1, 'Strong programming skills in Python, C++, or Java', 'technical', true),
(1, 'Experience with web development (React preferred)', 'technical', true),
(1, 'Understanding of algorithms and data structures', 'technical', true),
(1, 'Previous internship experience', 'experience', false),

(2, 'Pursuing MS/PhD in CS, ML, or related field', 'education', true),
(2, 'Strong Python programming', 'technical', true),
(2, 'Deep learning experience (PyTorch/TensorFlow)', 'technical', true),
(2, 'Published research', 'experience', false),

(3, 'MS in Data Science, Statistics, CS, or related field', 'education', true),
(3, 'Strong Python and SQL skills', 'technical', true),
(3, 'Experience with ML frameworks', 'technical', true),
(3, 'Statistical analysis and A/B testing knowledge', 'technical', true),
(3, 'Recommendation systems experience', 'experience', false),

(4, 'PhD student or recent graduate in ML/AI', 'education', true),
(4, 'Strong publication record in top venues', 'experience', true),
(4, 'Expertise in deep learning', 'technical', true),
(4, 'Novel research contributions', 'experience', true);

-- Insert sample generated materials
INSERT INTO generated_materials (opportunity_id, user_id, material_type, content) VALUES
(1, 1, 'subject_line', 'Software Engineering Intern Application - John Doe | Full-Stack Developer with Production Experience'),

(1, 1, 'email', 'Dear Meta Recruiting Team,

I am writing to express my strong interest in the Software Engineering Intern position at Meta. As a Computer Science student at University of Technology with hands-on experience in full-stack development and a passion for building user-facing products, I am excited about the opportunity to contribute to products used by billions of people worldwide.

During my internship at Tech Corp, I gained valuable experience building RESTful APIs using FastAPI and PostgreSQL, and developing React frontend components. My e-commerce platform project, which integrates payment processing and authentication deployed on AWS, demonstrates my ability to build scalable, production-ready applications. This experience aligns well with Meta''s focus on creating robust, user-centric products.

My technical skills include Python, JavaScript, TypeScript, React, and Node.js, along with strong foundations in algorithms and data structures (3.8 GPA). I have also contributed to research at my university lab, publishing 2 papers and mentoring junior students, which has strengthened my collaboration and communication skills.

I am particularly drawn to Meta''s mission of connecting people and building community. I would be thrilled to bring my full-stack development experience and eagerness to learn to your team.

Thank you for considering my application. I look forward to discussing how I can contribute to Meta''s innovative projects.

Best regards,
John Doe'),

(1, 1, 'fit_bullets', '• Built production RESTful APIs using FastAPI and PostgreSQL, directly applicable to Meta''s backend infrastructure
• Developed React frontend components with focus on user experience, aligning with Meta''s product philosophy
• Created full-stack e-commerce platform deployed on AWS with CI/CD, demonstrating end-to-end development capabilities
• Strong CS fundamentals with 3.8 GPA and experience in algorithms and data structures
• Published research and mentored students, showcasing collaboration and communication skills valued at Meta'),

(3, 2, 'subject_line', 'Data Science Intern Application - Jane Smith | MIT MS Student with Production Recommendation Systems Experience'),

(3, 2, 'email', 'Dear Netflix Data Science Team,

I am excited to apply for the Data Science Intern position at Netflix. As an MS Data Science student at MIT with direct experience building recommendation algorithms at scale, I am eager to contribute to Netflix''s world-class personalization and recommendation systems.

During my summer 2024 internship at Google, I developed recommendation algorithms serving over 10 million users and improved model accuracy by 15% using ensemble methods. This experience gave me hands-on expertise with production ML systems at scale, collaborative filtering, and A/B testing - skills that directly align with Netflix''s technical requirements.

My technical toolkit includes Python, TensorFlow, PyTorch, Scikit-learn, and extensive experience with large-scale data processing using Spark and Hadoop. I have deployed ML models to production using cloud platforms (GCP, AWS), ensuring scalability and reliability. Additionally, my research background at Stanford AI Lab, where I published 3 papers in top-tier conferences (NeurIPS, ICML), has equipped me with strong analytical and problem-solving skills.

I am particularly drawn to Netflix''s data-driven culture and commitment to delivering personalized experiences to members worldwide. The opportunity to work on recommendation systems that impact millions of users daily is incredibly exciting to me.

Thank you for considering my application. I would love to discuss how my recommendation systems experience and passion for data science can contribute to Netflix''s mission.

Best regards,
Jane Smith'),

(3, 2, 'fit_bullets', '• Developed recommendation algorithms at Google serving 10M+ users, directly applicable to Netflix''s personalization systems
• Improved model accuracy by 15% using ensemble methods, demonstrating ability to optimize production ML systems
• MS Data Science from MIT with strong foundation in statistical analysis and machine learning
• Expert in Python, TensorFlow, PyTorch, and large-scale data processing (Spark, Hadoop)
• Published 3 papers in top ML conferences (NeurIPS, ICML), showing research rigor and innovation
• Production ML deployment experience on cloud platforms (GCP, AWS) for scalable systems
• Cross-functional collaboration experience essential for Netflix''s team-oriented environment');

-- Verify data insertion
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Documents', COUNT(*) FROM documents
UNION ALL
SELECT 'Document Texts', COUNT(*) FROM document_texts
UNION ALL
SELECT 'Profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'Opportunities', COUNT(*) FROM opportunities
UNION ALL
SELECT 'Opportunity Requirements', COUNT(*) FROM opportunity_requirements
UNION ALL
SELECT 'Generated Materials', COUNT(*) FROM generated_materials;
