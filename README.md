# Compile-Mate

A robust code submission and evaluation platform that leverages Docker containers for secure code execution and evaluation. Think of it as a courthouse for code, where judges (different programming language environments) conduct their sessions in isolated containers.

## 🌟 Features

- **Secure Code Execution**: Utilizes Docker containers for isolated code execution
- **Multi-Language Support**: Run and evaluate code in multiple programming languages
- **Real-time Evaluation**: Instant feedback on code submissions
- **Resource Monitoring**: Track CPU, memory, and execution time
- **User Authentication**: Secure user management system
- **Problem Management**: Add, edit, and manage coding problems
- **Test Case Management**: Create and manage test cases for problems
- **Beautiful UI**: Modern and intuitive user interface
- **API Support**: RESTful API for integration with other services

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker 20.10 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/HarshaRockzz/Compile-Mate.git
cd Compile-Mate
```

2. Set up a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///db.sqlite3
```

5. Initialize the database:
```bash
python manage.py migrate
```

6. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 🐳 Docker Setup

The project uses Docker for code execution. Make sure Docker is running on your system.

1. Build and run with docker-compose:
```bash
docker-compose up --build
```

2. For production deployment:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🏗️ Project Structure

```
Compile-Mate/
├── CompileMate/          # Main project settings
├── Home/                 # Main application
│   ├── migrations/       # Database migrations
│   ├── admin.py         # Admin interface configuration
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   ├── tests.py         # Test cases
│   └── runcode.py       # Code execution logic
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker compose configuration
└── manage.py           # Django management script
```

## 🔧 Configuration

### Database Configuration
The project uses SQLite by default. To use PostgreSQL or other databases, update the `DATABASES` configuration in `settings.py`.

### Docker Configuration
- `Dockerfile`: Contains the main application container configuration
- `docker-compose.yml`: Defines the development environment services
- Language-specific Dockerfiles are located in their respective directories

## 🧪 Testing

1. Run the test suite:
```bash
python manage.py test
```

Note: Initial test runs may take longer as Docker images for different languages are downloaded.

2. Run specific tests:
```bash
python manage.py test Home.tests.TestClassName
```

## 📚 API Documentation

The API endpoints are documented using Swagger/OpenAPI. Access the documentation at:
- `/api/docs/` - Swagger UI
- `/api/schema/` - OpenAPI schema

Key endpoints:
- `/api/problems/` - Problem management
- `/api/submissions/` - Code submissions
- `/api/results/` - Submission results

## 🔐 Security

- Code execution is isolated in Docker containers
- Rate limiting is implemented on API endpoints
- Input validation and sanitization
- Secure secret management using environment variables
- Regular dependency updates and security patches

## 🎯 Problem Management

1. Add new problems using the admin interface or API
2. Problems can include:
   - Problem description (Markdown supported)
   - Input/Output specifications
   - Time and memory limits
   - Test cases
   - Sample solutions

## 💻 Supported Languages

- Python
- Java
- C++
- JavaScript (Node.js)
- Additional languages can be added by creating new Docker configurations

## 🔍 Monitoring and Logging

- Prometheus metrics available at `/metrics`
- Structured logging with JSON format
- APM integration for performance monitoring
- Resource usage tracking per submission

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community
- Docker community
- All contributors who have helped shape this project

## 🐛 Troubleshooting

### Common Issues

1. Docker Connection Issues
```bash
# Check Docker service status
sudo systemctl status docker
# Restart Docker service
sudo systemctl restart docker
```

2. Database Migration Issues
```bash
# Reset migrations
python manage.py migrate Home zero
python manage.py makemigrations
python manage.py migrate
```

3. Permission Issues
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the maintainers
- Check the [Wiki](wiki) for additional documentation

## 🚀 Deployment

### Production Deployment Checklist

1. Update `settings.py` with production settings
2. Configure environment variables
3. Set up a production database
4. Configure static file serving
5. Set up SSL/TLS certificates
6. Configure monitoring and logging
7. Set up backup systems

### Deployment Commands

```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn CompileMate.wsgi:application
```
