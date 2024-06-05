# Multimodal OpenAI Extractor

This is an extractor that supports multiple kinds of input documents like text, pdf and images and returns output in text using OpenAI. This extractor supports various OpenAI models like 3.5 Turbo and 4o and works on the Content of previous extractor as message, however we can manually overwrite prompt and message.

### Example:
##### input:
```
prompt = """Extract all text from the document."""
f = open("resume.pdf", "rb")
pdf_data = Content(content_type="application/pdf", data=f.read())
input_params = OAIExtractorConfig(prompt=prompt, model_name="gpt-4o")
extractor = OAIExtractor()
results = extractor.extract(pdf_data, params=input_params)
print(results)

prompt = """Extract all named entities from the text."""
article = Content.from_text("My name is Rishiraj and I live in India.")
input_params = OAIExtractorConfig(prompt=prompt)
extractor = OAIExtractor()
results = extractor.extract(article, params=input_params)
print(results)
```

##### output:
```
[Content(content_type='text/plain', data=b'First Last\nAdm. No. 22JEXXXX\nfirstlast@gmail.com\nXXX-XXX-XXXX\nlinkedin.com/in/firstlast\ngithub.com/firstlast\n\nEducation\nUniversity Name Expected May 20XX\nBachelor of Science in Computer Science (GPA: 4.00 / 4.00) City, State\n\xe2\x80\xa2 Relevant Coursework: Data Structures and Algorithms (C++), Prob & Stat in CS (Python), Intro to CS II (C++), Linear Algebra w/Computational Applications (Python)\n\nExperience\nCompany Name 1 Jan 20XX \xe2\x80\x93 May 20XX\nSoftware Engineer City, State\n\xe2\x80\xa2 Implemented microservices architecture using Node.js and Express, improving API response time by 25% and reducing server load by 30%.\n\xe2\x80\xa2 Led a cross-functional team in implementing a new feature using React and Redux, resulting in a 20% increase in user engagement within the first month.\n\xe2\x80\xa2 Optimized MySQL database queries, reducing page load times by 15% and enhancing overall application performance.\n\nProjects\nProject Name 1 | React.js, Angular, Vue.js, Django, Flask, Ruby on Rails\n\xe2\x80\xa2 Led the development of a microservices-based e-commerce platform using Node.js, resulting in a 40% increase in daily transactions within the first quarter.\n\xe2\x80\xa2 Designed and deployed a scalable RESTful API using Django and Django REST Framework, achieving a 30% improvement in data retrieval speed.\n\xe2\x80\xa2 Implemented a real-time chat feature using WebSocket and Socket.io, enhancing user engagement and reducing response time by 20%.\n\nProject Name 2 | Spring Boot, Express.js, TensorFlow, PyTorch, jQuery, Bootstrap\n\xe2\x80\xa2 Developed a data visualization dashboard using D3.js, providing stakeholders with real-time insights and improving decision-making processes.\n\xe2\x80\xa2 Built a CI/CD pipeline using Jenkins and Docker, reducing deployment time by 40% and ensuring consistent and reliable releases.\n\nTechnical Skills\nLanguages: Rust, Kotlin, Swift, Go, Scala, TypeScript, R, Perl, Haskell, Groovy, Julia, Dart\nTechnologies: React.js, Angular, Vue.js, Django, Flask, Ruby on Rails, Spring Boot, Express.js, TensorFlow, PyTorch, jQuery, Bootstrap, Laravel, Flask, ASP.NET, Node.js, Electron, Android SDK, iOS SDK, Symfony\nConcepts: Compiler, Operating System, Virtual Memory, Cache Memory, Encryption, Decryption, Artificial Intelligence, Machine Learning, Neural Networks, API, Database Normalization, Agile Methodology, Cloud Computing\n\nAchievements\n\xe2\x80\xa2 Pls Add your Achivements here e.g., Hackathons, Exam Ranks, etc.\n\nSocial Engagements\nVice-President: Of Association of Exploration Geophysicist - Student Chapter, IIT Dhanbad\nClub Member : at CYBER LABS - tech society of IIT Dhanbad\nVolunteer: at KARTAVYA - NGO run by students of IIT Dhanbad to educate underprivileged childrens.\nOrganisor:Concetto\xe2\x80\x9922 (Tech-fest) Khanan\xe2\x80\x9922 (Geo-Mining fest) .\nSports-Engagements: Badminton(state-level) , chess , cricket ,table-tennis.', features=[], labels={})]

[Content(content_type='text/plain', data=b'1. Rishiraj\n2. India', features=[], labels={})]
```