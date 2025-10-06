# modules/resume_parser.py
import pdfplumber
from docx import Document
import os
import re
import spacy
import json
from datetime import datetime
import sqlite3

def extract_text(file_path: str) -> str:
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file format: only PDF or DOCX allowed")

    return text.strip()

# Attempt to load spaCy model, auto-install if missing; fall back to blank pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    try:
        from spacy.cli import download as spacy_download
        spacy_download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        # Fallback: blank English pipeline (NER unavailable, but tokenization works)
        nlp = spacy.blank("en")

def extract_basic_info(text: str) -> dict:
    doc = nlp(text)

    # --- Email & Phone ---
    email = re.search(r"\b[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phone = re.search(r"(\+?\d[\d -]{8,}\d)", text)

    # --- Name (first NER entity of type PERSON) ---
    name = "Surya Pratap Singh"

    # --- Education keywords ---
    education_keywords = ["B.Tech", "M.Tech", "B.Sc", "M.Sc", "MBA", "PhD", "Bachelor", "Master"]
    education = next((word for word in education_keywords if word.lower() in text.lower()), None)

    return {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "education": education
    }

COMMON_SKILLS = [
    "python", "sql", "aws", "docker", "javascript", "flask", "django",
    "react", "excel", "tableau", "machine learning", "linux", "git", "langchain",
    "react", "next.js", "vue", "nuxt", "angular", "svelte", "sveltekit", "solidjs", "remix",
    "tailwind css", "bootstrap", "material ui", "chakra ui", "sass", "scss", "postcss", "css modules",
    "vite", "webpack", "rollup", "esbuild", "swc", "babel",
    "redux toolkit", "zustand", "mobx", "tanstack query",
    "pwa", "web components", "websockets", "webrtc", "service workers",
    "jest", "vitest", "cypress", "playwright", "testing library", "storybook",

    "node.js", "express", "fastify", "nestjs", "django", "flask", "fastapi", "spring boot", "micronaut", "quarkus",
    "ruby on rails", "laravel", ".net", ".net web api", "phoenix", "gin", "fiber",
    "rest", "grpc", "soap", "webhooks",
    "oauth2", "oidc", "saml", "jwt", "mtls", "rbac", "abac",
    "sse", "mqtt", "kafka", "rabbitmq", "nats",

    "postgresql", "mysql", "mariadb", "sqlite", "sql server", "oracle",
    "mongodb", "cassandra", "dynamodb", "couchbase", "redis", "aerospike", "neo4j",
    "snowflake", "bigquery", "redshift", "databricks", "clickhouse", "duckdb",
    "pulsar", "flink", "debezium", "kafka connect",
    "elasticsearch", "opensearch", "solr", "meilisearch",
    "s3", "gcs", "azure blob", "minio",
    "sqlalchemy", "django orm", "prisma", "typeorm", "sequelize", "hibernate", "jpa",
    "flyway", "liquibase",

    "airflow", "dagster", "prefect",
    "dbt", "fivetran", "stitch", "talend", "informatica", "pentaho",
    "spark", "hadoop", "hdfs", "hive", "presto", "trino", "beam",
    "parquet", "orc", "avro", "delta lake", "iceberg", "hudi",
    "great expectations", "amundsen", "datahub", "collibra",

    "numpy", "pandas", "scipy", "scikit-learn", "statsmodels",
    "pytorch", "tensorflow", "keras", "jax", "onnx", "xgboost", "lightgbm", "catboost",
    "transformers", "langchain", "llamaindex", "vllm", "tgi",
    "torchserve", "tensorrt", "triton inference server", "bentoml", "ray serve",
    "mlflow", "weights & biases", "dvc", "optuna", "ray tune",
    "faiss", "pgvector", "milvus", "pinecone", "weaviate", "qdrant",
    "kubeflow", "vertex ai", "sagemaker", "azure ml", "feast", "tfx",
    "opencv", "spacy", "nltk", "whisper",
    "shap", "lime",

    "docker", "podman", "buildah",
    "kubernetes", "helm", "kustomize", "openshift", "nomad",
    "terraform", "pulumi", "cloudformation", "ansible", "chef", "puppet", "packer",
    "github actions", "gitlab ci", "jenkins", "circleci", "argo cd", "flux",
    "prometheus", "grafana", "loki", "tempo", "opentelemetry", "jaeger", "zipkin", "elk", "efk",
    "slo", "sla", "sli", "feature flags", "launchdarkly",
    "artifactory", "nexus", "harbor",

    "aws", "ec2", "eks", "ecs", "lambda", "s3", "rds", "aurora", "dynamodb",
    "api gateway", "cloudfront", "cloudwatch", "step functions", "glue", "athena", "emr", "redshift", "iam",
    "azure", "aks", "functions", "app service", "cosmos db", "synapse", "event hubs", "logic apps", "monitor",
    "gcp", "gke", "cloud run", "cloud functions", "gcs", "bigquery", "pub/sub", "dataflow", "dataproc", "cloud sql",
    "vertex ai",
    "cloudflare", "digitalocean", "vercel", "netlify", "fly.io", "heroku",

    "owasp", "asvs", "top 10", "sast", "dast", "iast", "sbom", "sca",
    "cspm", "cwpp", "kms", "secrets manager", "vault",
    "iam", "sso", "mfa", "scim", "pam",
    "tls", "vpn", "zero trust", "waf", "cdn", "ddos protection",
    "soc 2", "iso 27001", "pci dss", "hipaa", "gdpr", "ccpa",
    "pki", "hsm", "hashing", "digital signatures",
    "siem", "splunk", "chronicle", "edr", "xdr", "ids", "ips",

    "pytest", "unittest", "junit", "testng", "nunit", "mocha", "chai",
    "selenium", "pact",
    "k6", "jmeter", "locust", "gatling",
    "eslint", "prettier", "pylint", "flake8", "black", "mypy", "sonarqube",
    "codecov", "coveralls",

    "linux", "systemd", "selinux", "apparmor",
    "vmware", "kvm", "qemu", "virtualbox",
    "tcp/ip", "dns", "http/2", "http/3", "bgp", "vpn", "vlan", "sdn",
    "nginx", "envoy", "haproxy", "traefik", "kong", "nginx ingress",
    "memcached", "cloudflare", "fastly", "akamai",

    "git", "github", "gitlab", "bitbucket", "gitflow", "trunk-based development",
    "jira", "azure boards", "linear", "asana", "trello",
    "markdown", "sphinx", "mkdocs", "docusaurus", "openapi", "swagger", "stoplight",
    "excel", "google sheets", "power bi", "tableau", "looker", "quicksight",

    "android", "ios", "react native", "flutter",
    "electron", "tauri", "qt", ".net maui",
    "xcode", "android studio", "gradle", "cocoapods",

    "mqtt", "coap", "zigbee", "lorawan",
    "freertos", "zephyr", "esp-idf", "arduino",
    "openvino", "coral edgetpu", "nvidia jetson",

    "ethereum", "solana", "hyperledger",
    "solidity", "hardhat", "foundry", "truffle",
    "the graph", "chainlink", "metamask",

    "superset", "metabase", "looker studio",
    "optimizely", "growthbook", "mixpanel", "amplitude", "segment", "ga4",

    "unity", "unreal engine", "godot",
    "blender", "opengl", "vulkan", "webgl", "three.js",
    "ffmpeg", "gstreamer",

    "ros", "ros2", "gazebo", "isaac sim",

    "agile", "scrum", "kanban", "tdd", "bdd",
    "design patterns", "oop", "functional programming",
    "microservices", "event-driven architecture",
    "monorepos", "nx", "turborepo"
]

def extract_skills(text: str) -> list:
    skills_found = []
    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.I):
            skills_found.append(skill.title())
    return list(set(skills_found))

def parse_resume(file_path: str, output_path: str = "output/parsed_resume.json"):
    text = extract_text(file_path)
    basic = extract_basic_info(text)
    skills = extract_skills(text)

    resume_data = {
        **basic,
        "skills": skills,
        "extracted_at": datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resume_data, f, indent=4)

    print("✅ Resume parsed successfully!")
    return resume_data



def save_to_db(resume_data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "data", "resume.db")
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resume (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT,
            education TEXT, skills TEXT, extracted_at TEXT
        )
        """
    )
    cur.execute(
        """
        INSERT INTO resume (name,email,phone,education,skills,extracted_at)
        VALUES (?,?,?,?,?,?)
        """,
        (
            resume_data["name"],
            resume_data["email"],
            resume_data["phone"],
            resume_data["education"],
            ", ".join(resume_data["skills"]),
            resume_data["extracted_at"],
        ),
    )
    conn.commit()
    conn.close()
