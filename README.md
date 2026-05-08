# 🎮 Telegram Quiz Bot - Advanced Game System

A professional, modern, and feature-rich Telegram Quiz Bot built with Python and Aiogram 3.x. This bot provides an engaging quiz experience with gamification elements, user profiles, leaderboards, achievements, and comprehensive admin panel.

## ✨ Features.

### 🎮 Core Quiz System
- **Multiple Game Modes**: Classic, Timed, Endless, Survival, Duel, Mixed
- **Category System**: Organized questions by categories
- **Difficulty Levels**: Easy, Medium, Hard with appropriate rewards
- **Real-time Quiz**: Interactive questions with time limits
- **Answer Validation**: Instant feedback with explanations
- **Progress Tracking**: Live quiz progress and statistics

### 🏆 Gamification
- **XP System**: Experience points for correct answers
- **Level Progression**: Level up with rewards and unlockables
- **Coin Economy**: Virtual currency for rewards and features
- **Achievement System**: Unlockable achievements with rewards
- **Daily Streaks**: Consecutive login bonuses
- **Leaderboards**: Global and category-specific rankings

### 👤 User Features
- **User Profiles**: Comprehensive statistics and progress
- **Customization**: Personal settings and preferences
- **Referral System**: Invite friends for bonuses
- **Daily Bonuses**: Claim rewards every day
- **Achievement Tracking**: View and unlock achievements
- **Statistics**: Detailed performance analytics

### 👑 Admin Panel
- **User Management**: Ban, unban, premium status
- **Content Management**: Add/edit questions and categories
- **Broadcast System**: Send messages to users
- **Analytics Dashboard**: Comprehensive statistics
- **Database Management**: Backup and restore operations
- **System Configuration**: Bot settings and parameters

### 🔧 Technical Features
- **Async Architecture**: High-performance async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for performance optimization
- **Scheduler**: APScheduler for automated tasks
- **Migrations**: Alembic for database versioning
- **Docker Support**: Complete containerization
- **Logging**: Comprehensive logging system
- **Rate Limiting**: Anti-spam protection
- **FSM States**: Advanced conversation management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional but recommended)

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd telegram-quiz-bot
```

#### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

#### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
```

#### 4. Database Setup
```bash
# Create PostgreSQL database
createdb quizbot

# Run database migrations
alembic upgrade head
```

#### 5. Start the Bot
```bash
# Run directly
python bot/bot.py

# Or with Docker Compose
docker-compose up -d
```

## 📋 Environment Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/quizbot
POSTGRES_USER=quizbot
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=quizbot

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Bot Settings
DEBUG=False
LOG_LEVEL=INFO
MAX_QUESTIONS_PER_GAME=20
QUESTION_TIME_LIMIT=30
DAILY_BONUS_COINS=100
REFERRAL_BONUS=50

# Game Configuration
XP_PER_CORRECT_ANSWER=10
XP_PER_STREAK_DAY=5
LEVEL_UP_BONUS=500
ACHIEVEMENT_BONUS=200

# Scheduler Configuration
SCHEDULER_ENABLED=True
DAILY_RESET_TIME=00:00

# Security
RATE_LIMIT_PER_SECOND=5
RATE_LIMIT_PER_MINUTE=30
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Run Database Migrations**
   ```bash
   docker-compose exec bot alembic upgrade head
   ```

4. **Check Logs**
   ```bash
   docker-compose logs -f bot
   ```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f bot

# Execute commands in bot container
docker-compose exec bot python -c "print('Hello')"

# Restart bot
docker-compose restart bot
```

## 📊 Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**
   ```bash
   sudo -u postgres createdb quizbot
   sudo -u postgres createuser --interactive
   ```

3. **Configure Connection**
   Update `DATABASE_URL` in `.env` file.

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

## 🎯 Bot Commands

### User Commands
- `/start` - Start the bot and register
- `/help` - Show help information
- `/profile` - View your profile
- `/leaderboard` - View leaderboards
- `/daily` - Claim daily bonus
- `/quiz` - Start a quiz
- `/cancel` - Cancel current action

### Admin Commands
- `/admin` - Open admin panel
- `/broadcast` - Send broadcast message
- `/stats` - View bot statistics
- `/users` - Manage users

## 🏗️ Project Structure

```
telegram-quiz-bot/
├── bot/                 # Bot core and configuration
├── handlers/            # Message and callback handlers
├── middlewares/          # Custom middlewares
├── keyboards/           # Inline and reply keyboards
├── states/              # FSM state definitions
├── services/            # Business logic services
├── database/            # Database configuration
├── models/              # SQLAlchemy models
├── utils/               # Utility functions
├── filters/             # Custom filters
├── config/              # Configuration settings
├── assets/              # Static assets
├── logs/                # Log files
├── alembic/             # Database migrations
├── docker/              # Docker configurations
└── tests/               # Test files
```

## 🔧 Configuration

### Bot Settings
- **Debug Mode**: Enable/disable debug features
- **Log Level**: Set logging verbosity
- **Rate Limiting**: Configure anti-spam limits
- **Admin IDs**: Set administrator user IDs

### Game Settings
- **Max Questions**: Maximum questions per game
- **Time Limits**: Question time limits
- **XP Rewards**: Experience point rewards
- **Coin Rewards**: Currency rewards
- **Daily Bonus**: Daily login bonus amount

### Database Settings
- **Connection**: PostgreSQL connection string
- **Pool Size**: Database connection pool size
- **Timeout**: Connection timeout settings

## 📈 Monitoring and Logging

### Log Files
- `logs/bot.log` - Main bot log
- `logs/error.log` - Error log
- `logs/access.log` - Access log

### Health Checks
- Bot health check endpoint
- Database connection monitoring
- Redis connection monitoring

### Metrics
- User activity statistics
- Game performance metrics
- System resource usage

## 🔒 Security

### Rate Limiting
- Per-second rate limits
- Per-minute rate limits
- User-specific limits

### Input Validation
- Message content validation
- Callback data validation
- SQL injection prevention

### Admin Protection
- Admin-only commands
- Sensitive operation confirmation
- Action logging

## 🚀 Performance Optimization

### Caching
- Redis caching for frequent data
- Leaderboard caching
- Category statistics caching

### Database Optimization
- Optimized queries
- Connection pooling
- Index optimization

### Async Operations
- Async/await throughout
- Concurrent processing
- Non-blocking I/O

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=bot

# Run specific test
python -m pytest tests/test_handlers.py
```

### Test Coverage
- Handler testing
- Service testing
- Model testing
- Integration testing

## 📝 Development

### Adding New Features
1. Create handlers in `handlers/`
2. Add models in `models/`
3. Create services in `services/`
4. Add keyboards in `keyboards/`
5. Update states in `states/`

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings
- Write tests

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Starting
- Check BOT_TOKEN in .env
- Verify database connection
- Check log files for errors

#### Database Issues
- Verify PostgreSQL is running
- Check connection string
- Run migrations

#### Redis Issues
- Verify Redis is running
- Check connection URL
- Test Redis connectivity

#### Permission Issues
- Check file permissions
- Verify user permissions
- Check Docker user settings

### Debug Mode
Enable debug mode in `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📞 Support

### Getting Help
- Check the documentation
- Review log files
- Check GitHub issues
- Contact development team

### Reporting Issues
- Include error logs
- Describe reproduction steps
- Specify environment details
- Include configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Aiogram framework for Telegram bot development
- SQLAlchemy for database ORM
- Redis for caching
- APScheduler for task scheduling
- Docker for containerization

## 🔄 Updates

### Version History
- v1.0.0 - Initial release
- v1.1.0 - Added achievement system
- v1.2.0 - Enhanced admin panel
- v1.3.0 - Performance optimizations

### Upcoming Features
- Tournament system
- Multiplayer quizzes
- Voice questions
- API integration
- Mobile app

---

**🎮 Start building your quiz bot empire today!**
