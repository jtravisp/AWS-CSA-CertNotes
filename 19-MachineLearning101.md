# Machine Learning 101

## Amazon Comprehend
Amazon Comprehend is a natural-language processing (NLP) service that uses machine learning to uncover valuable insights and connections in text.

- Input a document, it develops insights
- Natural Language Processing (NLP)
- Input = Document (text)
- Output = Entities, phrases, language, PII, sentiments
- Pre-trained models or Custom
- Real-time analysis for small workloads
- Async jobs for larger workloads
- Console and CLI... interactive or use APIs to build into apps

- Comprehend Console... Launch...
  - sample text provided, built-in or custom analysis types
  - Analyze...
    - Entity- persons, organization; Confidence level 0.00-1.00
    - Languages used
    - Key phrases
    - PII- names, credit card/bank numbers, phone, email, etc
    - Sentiment- neutral, positive, negative, mixed

## Amazon Kendra
Amazon Kendra is an intelligent search service powered by machine learning (ML).

- Designed to mimic interacting with a human expert
- supports a wide range of question types
- Factoid- Who, What, Where
- Descriptive- How do I get....?
- Keyword- What time is the keynote address?
  - address can have multiple meanings- Kendra helps determine intent

- Index- searchable data organized in an effiecient way
- Date source- where data lives- Kendra connects and indexes from this location
- S3, Confluence, Google Workspace, RDS, OneDrive, Salesforce, Kendra web crawler, Workdocs, FSX...
- Sync with index based on a schedule
- Documents- Structures (FAQs), Unstructured (e.g. HTML, PDFs, text...)
- Integreates with AWS services (IAM, Identity Center (SSO),...)

## Amazon Lex
Fully managed artificial intelligence (AI) service with advanced natural language models to design, build, test, and deploy conversational interfaces in applications.

- Text or Voice conversational interfaces
- Powers the Alexa service
- Automatic speech recognition (ASR)- speech to text
- Natural Language Understanding (NLU)- intent
  - understands context of each following statement
  - build understanding into your application
- Scales, integrates, quick to deploy, pay as you go
- Use for chatbots, voice assistants, Q&A bots, Info/Enterprise bots

Concepts
- Lex provides bots... conversing ni 1+ languages
- Intent.. ana ction the user wants to perform
- ...e.g. order a pizza
- Sample utterances... ways in which an intent might be said- "Can I order...", "I want to order", "Give me a...", etc
- How to fufill the intent... Lambda integration
- Slot (parameters) e.;g. Size small/med/lg, Crust normal/thin

## Amazon Polly
Service that turns text into lifelike speech, allowing you to create applications that talk, and build entirely new categories of speech-enabled products.

- converts text into "life-like" speech
- Text (language) -> Speech (language) - NO translation
- Standard TTS = Concatenative (phonemes)
- Neural TTS = phonemes -> spectograms -> vocoder -> audio
- Output- MP3... Ogg Vorbis... PCM

- Speech Synthesis Markup Language (SSML)
- ...additional control over how Polly generates speech
- ...emphasis, pronunciation, whispering, "Newscaster" speaking style

## Amazon Rekognition
Offers pre-trained and customizable computer vision (CV) capabilities to extract information and insights from your images and videos.

- Deep learning Image and Video analysis
- ID objects, people, text, activities, content moderation, face detection, aalysis, comparison, pathing, more...
- Per image or Per minute (video) pricing
- Integrates withs apps and event driven
- Can analyze live video stream - kinesis video streams

- Image uploaded to S3 -> S3 Event invokes Lambda -> Rekognition IDs animals -> Metadata stored in DDB

## Amazon Textract
Machine learning (ML) service that automatically extracts text, handwriting, and data from scanned documents. It goes beyond simple optical character recognition (OCR) to identify, understand, and extract data from forms and tables.

- Detect and analyze text
- Input = JPEG, PNG, PDF, TIFF
- Output = Extracted text, structure, and analysis
- Most documents = Synchronous (real-time)
- Large docs (big PDFs) = Asynchronous
- Pay per usage... custom pricing for large volumes

- Detection of text
- ...relationship between text, interaction between elements
- ...metadata i.e. where text occurs
- Document Analysis (names, address...)
- Receipt Analysis (prices, vendor, line items...)
- Identity Documents (Abstract fields... DocumentID)

Example
- Textract console.. Try...
  - example image
  - can extract table structure along with data
- could use for ID verification

## Amazon Transcribe
Automatic speech recognition service that uses machine learning models to convert audio to text. You can use Amazon Transcribe as a standalone transcription service or to add speech-to-text capabilities to any application.

- Automatic Speech Recognition (ASR) service
- Input = audio, Output = text
- Language customization, filters for privacy, audience appropriate language, speaker identification
- Pay per user... per second of transcribed audio

Use Cases
- Full text indexing of audio- allow searching
- Meeting notes
- Subtitles/captions and transcripts
- Callanalytics (characteristics, summarization, categories, and sentiment)
- Integration with other apps/AWS ML services

## Amazon Translate
Neural machine translation service that delivers fast, high-quality, affordable, and customizable language translation.

- Text translation service... ML based
- From native lanuage to other languages
- Encoder reads source -> semantic representation (meaning)
- Decoder reads meaning -> writes target language
- Attention mechanisms ensure "meaning" is translated
- Auto detect source text language

Use Cases
- Multilingual user experience
- ...meeting notes, posts, communications, articles
- emails, in-game chat, customer live chat
- Translate incoming data (social media/news/comms)
- Language-independence for other AWS services
- ...comprehend, transcribe, polly, data stored in S3, RDS, DDB
- Commonly integrates with other services/apps/platforms

## Amazon Forecast 101
Fully managed service that uses statistical and machine learning algorithms to deliver highly accurate time-series forecasts.

- Forecasting for time-series date
- ...retail demand, supply chain, staffing, energy, server capacity, web traffic...
- Import historical and related data
- ...understands what is normal
- Output = forecast and forecast explainability
- Web console (visualization), CLI, APIs, Python SDK

## Amazon Fraud Detector
Fully managed fraud detection service that automates the detection of potentially fraudulent activities online. These activities include unauthorized transactions and the creation of fake accounts. Amazon Fraud Detector works by using machine learning to analyze your data.

- Fully managed Fraud Detection service
- ...new account creations, payments, guest checkout
- Upload historical data, choose model
- ...Online Fraud - little historical data, e.g. new customer
- ...Transaction Fraud- transactional history, ID suspect payments
- ...Account Takeover- ID phishing or another social based attack
- Things are scored... Rules/Decision Logic allow you to react to a score

## Amazon SageMaker
Fully managed machine learning service. With SageMaker, data scientists and developers can quickly and easily build and train machine learning models, and then directly deploy them into a production-ready hosted environment.

- collection of products and features
- Fully Managed ML Service
- Fetch, Clean, Prepare, Tain, Evaluate, Deploy, Monitor/Collect
- Sage Maker Studio - Build, train, debug, and monitor models - IDE for ML lifecycle
- Sage Maker Domain - EFS Volume, Users, Apps, Policies, VPCs.. isolation
- Containers- Docker containers deployed to ML EC2 instance- ML environments (OS, Libs, Tooling)
- Hosting- Deploy endpoints for your models
- Sage Maker has no cost- the reources it creates do (COMPLEX pricing)

## Other Service- AWS Local Zones
AWS Local Zones are a type of infrastructure deployment that places compute, storage, database, and other select AWS services close to large population and industry centers.

AWS w/o Local Zones
- us-west-2
  - 3 AZs- us-west-2a, us-west-2b, us-west-2c
  - VPC across all 3 AZs
  - outside VPC - AWS Public Zone
  - resilient to failure
- effects of geographic distance?
  - AZ might be 100s of miles from business premises, can make a difference

- Local Zones
  - add subnets in VPC in each AZ
  - local zone: us-west-2-las-1 (Las Vegas)
  - can have multiple local zones in a given city
    - us-west-2-lax-1a, us-west-2-lax-1b
  - diff services use local zones in diff ways
  - VPC is extended into local zones
  - benefit is super low latency, smaller geographic seperation
- Subnets created in local zones behave just like those in parent region
- EBS Snapshots? uses S3 in parent region

Summary Points
- "1" zone... so no built in resilience
- Think of them like an AZ, but near your location
- They are closer to you... so lower latency
- Not all rpoducts support them... many are opt in w/ limitations
- Direct Connect (DX) to a local zone IS supported (extreme performance needs)
- Utilize parent region.. i.e. EBS Snapshots are TO arent
- Use local zones when you need the HIGHEST performance
