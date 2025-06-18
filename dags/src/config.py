"""
Configuration constants for the daily papers parser
"""

# Data sources
DATA_SOURCES = {
    "huggingface": "https://huggingface.co/papers",
    "arxiv_lg": "https://arxiv.org/list/cs.LG/recent",
    "arxiv_ai": "https://arxiv.org/list/cs.AI/recent", 
    "arxiv_ro": "https://arxiv.org/list/cs.RO/recent",
    "arxiv_dc": "https://arxiv.org/list/cs.DC/recent",
    "arxiv_et": "https://arxiv.org/list/cs.ET/recent"
}

# MLOps/LLMOps keywords for classification
MLOPS_KEYWORDS = [
    'mlops', 'ml ops', 'machine learning operations', 'llmops', 'llm ops',
    'model deployment', 'model serving', 'model monitoring', 'model versioning',
    'feature store', 'experiment tracking', 'hyperparameter tuning',
    'distributed training', 'model registry', 'continuous integration',
    'continuous deployment', 'ci/cd', 'kubernetes', 'docker', 'containerization',
    'orchestration', 'pipeline', 'workflow', 'airflow', 'kubeflow', 'mlflow',
    'wandb', 'tensorboard', 'model management', 'data versioning', 'dvc',
    'model optimization', 'quantization', 'pruning', 'distillation',
    'inference optimization', 'edge deployment', 'federated learning',
    'distributed systems', 'scalability', 'reliability', 'observability',
    'monitoring', 'logging', 'metrics', 'alerting', 'auto-scaling',
    'resource management', 'gpu scheduling', 'cluster management'
]

# Common tools and technologies regex patterns
TOOLS_PATTERNS = [
    r'\b(?:TensorFlow|PyTorch|Keras|Scikit-learn|XGBoost|LightGBM)\b',
    r'\b(?:Docker|Kubernetes|Helm|Istio)\b', 
    r'\b(?:MLflow|Kubeflow|Airflow|Prefect|Dagster)\b',
    r'\b(?:Weights & Biases|WandB|TensorBoard|Neptune)\b',
    r'\b(?:Ray|Dask|Spark|Hadoop|Kafka)\b',
    r'\b(?:AWS|GCP|Azure|S3|BigQuery|Redshift)\b',
    r'\b(?:Python|R|Scala|Java|Go|Rust)\b',
    r'\b(?:FastAPI|Flask|Django|Streamlit|Gradio)\b',
    r'\b(?:PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
    r'\b(?:Prometheus|Grafana|ELK|Jaeger)\b'
]

# Request headers for web scraping
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Parsing limits
MAX_PAPERS_PER_SOURCE = 20
REQUEST_TIMEOUT = 30

# Rate limiting for individual paper requests
ARXIV_REQUEST_DELAY = 0.5  # Seconds between requests to be respectful to ArXiv servers 
