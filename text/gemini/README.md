# Multimodal Gemini Extractor

This is an extractor that supports multiple kinds of input documents like text, pdf and images and returns output in text using Gemini from Google. This extractor supports various Gemini models like 1.5 Pro and 1.5 Flash and works on the Content of previous extractor as message, however we can manually overwrite prompt and message. Gemini has 1 million token context window that can process vast amounts of information in one go — including 11 hours of audio transcript, codebases with over 30,000 lines of code or over 700,000 words.

### Example:
##### input:
```
prompt = """Extract all text from the document."""
f = open("resume.pdf", "rb")
pdf_data = Content(content_type="application/pdf", data=f.read())
input_params = GeminiExtractorConfig(prompt=prompt)
extractor = GeminiExtractor()
results = extractor.extract(pdf_data, params=input_params)
print(results)

prompt = """Extract all named entities from the text."""
article = Content.from_text("My name is Rishiraj and I live in India.")
input_params = GeminiExtractorConfig(prompt=prompt)
extractor = GeminiExtractor()
results = extractor.extract(article, params=input_params)
print(results)
```

##### output:
```
Uploaded file 'tmpe3kd797x.jpg' as: https://generativelanguage.googleapis.com/v1beta/files/7mccy2bjij87
[Content(content_type='text/plain', data=b"**First Last**\n\nAdm. No. 22JEXXXX  \nfirstlast@gmail.com  \nXXX-XXX-XXXX  \nlinkedin.com/in/firstlast  \ngithub.com/firstlast\n\n**Education**\n\n**University Name**\nBachelor of Science in Computer Science (GPA: 4.00 / 4.00)\n* **Relevant Coursework:** Data Structures and Algorithms (C++), Prob & Stat in CS (Python), Intro to CS II (C++), Linear Algebra w/Computational Applications (Python)\n\nExpected | May 20XX\n------- | --------\nCity, State\n\n**Experience**\n\n**Company Name 1**\nSoftware Engineer | Jan 20XX - May 20XX\n------- | --------\nCity, State\n* Implemented microservices architecture using Node.js and Express, improving API response time by 25% and reducing server load by 30%.\n* Led a cross-functional team in implementing a new feature using React and Redux, resulting in a 200% increase in user engagement within the first month.\n* Optimized MySQL database queries, reducing page load times by 15% and enhancing overall application performance.\n\n**Projects**\n\n**Project Name 1** | React.js, Angular, Vue.js, Django, Flask, Ruby on Rails\n------- | --------\n* Led the development of a microservices-based e-commerce platform using Node.js, resulting in a 40% increase in daily transactions within the first quarter.\n* Designed and deployed a scalable RESTful API using Django and Django REST Framework, achieving a 30% improvement in data retrieval speed.\n* Implemented a real-time chat feature using WebSocket and Socket.io, enhancing user engagement and reducing response time by 20%.\n\n**Project Name 2** | Spring Boot, Express.js, TensorFlow, PyTorch, jQuery, Bootstrap\n------- | --------\n* Developed a data visualization dashboard using D3.js, providing stakeholders with real-time insights and improving decision-making processes.\n* Built a CI/CD pipeline using Jenkins and Docker, reducing deployment time by 40% and ensuring consistent and reliable releases.\n\n**Technical Skills**\n\n**Languages:** Rust, Kotlin, Swift, Go, Scala, TypeScript, R, Perl, Haskell, Groovy, Julia, Dart\n**Technologies:** React.js, Angular, Vue.js, Django, Flask, Ruby on Rails, Spring Boot, Express.js, TensorFlow, PyTorch, jQuery, Bootstrap, Laravel, Flask, ASP.NET, Node.js, Electron, Android SDK, iOS SDK, Symphony\n**Concepts:** Compiler, Operating System, Virtual Memory, Cache Memory, Encryption, Decryption, Artificial Intelligence, Machine Learning, Neural Networks, API, Database Normalization, Agile Methodology, Cloud Computing\n\n**Achievements**\n\n* Pls Add your Achievements here e.g., Hackathons, Exam Ranks, etc.\n\n**Social Engagements**\n\n**Vice-President:** Of Association of Exploration Geophysicist - Student Chapter, IIT Dhanbad\n**Club Member:** at CYBER LABS - tech society of IIT Dhanbad\n**Volunteer:** at KARTAVYA - NGO run by students of IIT Dhanbad to educate underprivileged childrens.\n**Organiser:** Concetto'22 (Tech-fest) Khanan'22 (Geo-Mining fest).\n**Sports-Engagements:** Badminton(state-level), chess, cricket, table-tennis. \n", features=[], labels={})]

[Content(content_type='text/plain', data=b'The named entities in the text are:\n\n* **Rishiraj:** Person\n* **India:** Location \n', features=[], labels={})]
```