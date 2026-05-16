

import json
import os

# Known SHL Individual Test Solutions 
FALLBACK_CATALOG = [
    {
        "name": "Verify - Numerical Ability",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-numerical-ability/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures ability to work with numerical data in workplace context. Assesses numerical reasoning, calculations, and interpreting statistics.",
        "job_levels": ["Entry-Level", "Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director"],
        "languages": ["English", "French", "German", "Spanish", "Arabic", "Chinese Simplified"]
    },
    {
        "name": "Verify - Verbal Reasoning",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-verbal-reasoning/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses ability to understand written information and evaluate arguments. Measures verbal comprehension and critical reasoning.",
        "job_levels": ["Entry-Level", "Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English", "French", "German", "Spanish", "Dutch"]
    },
    {
        "name": "Verify - Inductive Reasoning",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-inductive-reasoning/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures ability to identify patterns and rules in abstract information. Assesses logical and analytical thinking.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "Verify - Deductive Reasoning",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-deductive-reasoning/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses ability to draw logical conclusions from given information. Tests deductive and analytical reasoning skills.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "OPQ32r",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/opq32r/",
        "test_type": "P",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Occupational Personality Questionnaire. Measures 32 personality characteristics relevant to work behavior, performance, and relationships.",
        "job_levels": ["Entry-Level", "Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director", "Executive"],
        "languages": ["English", "French", "German", "Spanish", "Chinese Simplified", "Arabic", "Dutch", "Italian", "Japanese", "Korean", "Portuguese"]
    },
    {
        "name": "MQ (Motivation Questionnaire)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/motivation-questionnaire-mq/",
        "test_type": "P",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses motivational factors that drive an individual's behavior at work. Identifies what motivates and de-motivates the candidate.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director"],
        "languages": ["English", "French", "German", "Spanish", "Dutch"]
    },
    {
        "name": "Verify G+ (General Ability)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-g-plus-general-ability/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": True,
        "description": "Comprehensive cognitive ability test combining numerical, verbal, and inductive reasoning. Best for professional and managerial roles.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director", "Executive"],
        "languages": ["English", "French", "German", "Spanish", "Chinese Simplified"]
    },
    {
        "name": "Java 8 (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Tests knowledge and skills in Java 8 programming language including OOP concepts, collections, streams, and best practices.",
        "job_levels": ["Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Core Java (Advanced Level)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-advanced-level-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Advanced assessment of Core Java skills including multithreading, design patterns, JVM internals, and performance optimization.",
        "job_levels": ["Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English"]
    },
    {
        "name": "Python (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/python-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Tests Python programming skills including data structures, OOP, libraries, and scripting capabilities.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "SQL (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/sql-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses SQL querying skills including SELECT statements, JOINs, subqueries, aggregation, and database management.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "JavaScript (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/javascript-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Tests JavaScript programming knowledge including DOM manipulation, async programming, ES6+ features, and frameworks.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Entry Level Sales Solution",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/entry-level-sales-solution/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Comprehensive assessment for entry-level sales roles measuring personality traits, situational judgment, and cognitive ability relevant to sales success.",
        "job_levels": ["Entry-Level"],
        "languages": ["English"]
    },
    {
        "name": "Sales Representative Solution",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/sales-representative-solution/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Evaluates competencies critical for sales representatives including persuasion, resilience, customer focus, and results orientation.",
        "job_levels": ["Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English", "Spanish", "French"]
    },
    {
        "name": "Situational Judgement Test - Customer Service",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/customer-service-situational-judgement-test/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures judgment in realistic customer service scenarios. Tests handling of difficult customers, complaint resolution, and service quality.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "French", "Spanish", "German"]
    },
    {
        "name": "Situational Judgement Test - Management",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/management-situational-judgement-test/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses management judgment in realistic workplace scenarios including team management, conflict resolution, and decision-making.",
        "job_levels": ["Manager", "Front Line Manager", "Supervisor"],
        "languages": ["English", "French", "German"]
    },
    {
        "name": "Verify Interactive - Numerical Reasoning",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-interactive-numerical-reasoning/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": True,
        "description": "Mobile-first interactive numerical reasoning assessment. Uses workplace-relevant scenarios and adaptive technology for accurate measurement.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "Verify Interactive - Deductive Reasoning",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-interactive-deductive-reasoning/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": True,
        "description": "Mobile-first interactive deductive reasoning test using adaptive item response theory for precise ability measurement.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "Workplace English Language Test (WELT)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/workplace-english-language-test/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses English language proficiency in workplace context. Tests reading, listening, and writing skills required for professional roles.",
        "job_levels": ["Entry-Level", "General Population", "Graduate", "Mid-Professional"],
        "languages": ["English"]
    },
    {
        "name": "Graduate Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/graduate-short-form/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Efficient screening tool for graduate recruitment combining verbal, numerical, and inductive reasoning in a short format.",
        "job_levels": ["Graduate"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "Automata Fix",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/automata-fix/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Coding simulation assessment where candidates fix broken code. Tests practical debugging and problem-solving skills for developers.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Automata Selenium",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/automata-selenium/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Selenium-based coding assessment for QA and test automation roles. Tests ability to write and fix Selenium test scripts.",
        "job_levels": ["Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Smart Interview Live",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/smart-interview-live/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Live video interview with AI-powered behavioral analysis. Evaluates competencies through structured interview questions.",
        "job_levels": ["Entry-Level", "Graduate", "Mid-Professional"],
        "languages": ["English", "French", "German"]
    },
    {
        "name": "Smart Interview On Demand",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/smart-interview-on-demand/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Pre-recorded video interview with AI scoring. Candidates answer structured questions at their convenience; AI evaluates responses.",
        "job_levels": ["Entry-Level", "Graduate", "Mid-Professional"],
        "languages": ["English", "French", "Spanish"]
    },
    {
        "name": "Coding Simulation - Front End",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/coding-simulation-front-end/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Hands-on coding simulation for front-end development roles. Tests HTML, CSS, JavaScript, and React skills through real tasks.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Coding Simulation - Back End",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/coding-simulation-back-end/",
        "test_type": "S",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Hands-on coding simulation for back-end roles. Tests API development, database queries, and server-side logic.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Financial Professional - Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/financial-professional-short-form/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Cognitive screening for financial roles combining numerical and verbal reasoning in a concise format.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Global Skills Assessment (GSA)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/global-skills-assessment/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": True,
        "description": "Adaptive global cognitive assessment measuring core skills across numerical, verbal, and abstract reasoning. Suitable for all levels globally.",
        "job_levels": ["Entry-Level", "General Population", "Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English", "French", "German", "Spanish", "Arabic", "Chinese Simplified", "Japanese", "Portuguese"]
    },
    {
        "name": "Occupational Personality Questionnaire (OPQ)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/opq/",
        "test_type": "P",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures 32 personality traits relevant to workplace performance. Provides insights into behavior, communication, and leadership style.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor", "Manager", "Director", "Executive"],
        "languages": ["English", "French", "German", "Spanish", "Dutch", "Arabic", "Chinese", "Japanese"]
    },
    {
        "name": "Dependability and Safety Instrument (DSI)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/dependability-and-safety-instrument/",
        "test_type": "P",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures attitudes toward workplace safety, dependability, and integrity. Ideal for safety-critical and operational roles.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "Spanish"]
    },
    {
        "name": "Service - Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/service-short-form/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Screens candidates for customer-facing roles by measuring service orientation, reliability, and interpersonal skills.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "French", "Spanish"]
    },
    {
        "name": "Microsoft Excel (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/microsoft-excel-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Tests proficiency in Microsoft Excel including formulas, pivot tables, data analysis, and advanced features.",
        "job_levels": ["Entry-Level", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Microsoft Word (New)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/microsoft-word-new/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses Microsoft Word proficiency including formatting, styles, mail merge, and document management.",
        "job_levels": ["Entry-Level", "General Population", "Mid-Professional"],
        "languages": ["English"]
    },
    {
        "name": "Data Entry Speed and Accuracy",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/data-entry-speed-and-accuracy/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures typing speed and accuracy for data entry roles. Tests keyboard proficiency and attention to detail.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English"]
    },
    {
        "name": "Mechanical Comprehension Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/mechanical-comprehension-test/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses understanding of mechanical and physical concepts. Ideal for engineering, maintenance, and technical roles.",
        "job_levels": ["Entry-Level", "General Population", "Mid-Professional"],
        "languages": ["English"]
    },
    {
        "name": "Checking (Verify)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-checking/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Measures speed and accuracy in checking numerical and verbal information. Tests attention to detail for clerical roles.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "French", "German", "Spanish"]
    },
    {
        "name": "Calculation (Verify)",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/verify-calculation/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Tests basic arithmetic and numerical calculation skills without a calculator. For roles requiring mental math.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "French", "German"]
    },
    {
        "name": "Agile Developer",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/agile-developer/",
        "test_type": "K",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Assesses knowledge of Agile methodologies, Scrum, Kanban, and DevOps practices for software development teams.",
        "job_levels": ["Mid-Professional", "Professional Individual Contributor", "Manager"],
        "languages": ["English"]
    },
    {
        "name": "Technology Professional Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/technology-professional-short-form/",
        "test_type": "A",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Quick cognitive screening for technology roles combining inductive and numerical reasoning in a compact format.",
        "job_levels": ["Graduate", "Mid-Professional", "Professional Individual Contributor"],
        "languages": ["English"]
    },
    {
        "name": "Workplace Safety Assessment",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/workplace-safety-assessment/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Evaluates safety attitudes, behaviors, and risk awareness. Used in manufacturing, construction, and high-risk environments.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "Spanish"]
    },
    {
        "name": "Call Center - Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/call-center-short-form/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Designed for call center hiring. Measures customer focus, communication, and resilience traits relevant to contact center success.",
        "job_levels": ["Entry-Level", "General Population"],
        "languages": ["English", "Spanish", "French"]
    },
    {
        "name": "Administrative Professional Short Form",
        "url": "https://www.shl.com/solutions/products/product-catalog/view/administrative-professional-short-form/",
        "test_type": "B",
        "remote_testing": True,
        "adaptive_irt": False,
        "description": "Screens candidates for administrative roles by assessing organization, attention to detail, and professional skills.",
        "job_levels": ["Entry-Level", "General Population", "Mid-Professional"],
        "languages": ["English"]
    },
]


def save_fallback(path: str = "data/shl_catalog.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(FALLBACK_CATALOG, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(FALLBACK_CATALOG)} fallback items to {path}")


if __name__ == "__main__":
    save_fallback()
    print("Fallback catalog ready!")
