# Architecture Documentation

This document describes the clean architecture and design patterns used in the rotation bot.

## Overview

The codebase follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│           CLI Interface (bot_simple.py)      │
│                                              │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│         Application Layer (bot.py)           │
│         • RotationBot (Orchestrator)         │
│         • Dependency Injection               │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
   ┌──────┐ ┌──────┐ ┌──────────┐
   │Config│ │Service│ │Notification│
   │Layer │ │Layer  │ │  Layer     │
   └──────┘ └──────┘ └──────────┘
```

---

## Design Patterns Used

### 1. **Dependency Injection**

The `RotationBot` class receives all its dependencies through the constructor:

```python
class RotationBot:
    def __init__(
        self,
        config: BotConfig,
        rotation_service: RotationService,
        message_service: MessageService,
        notification_service: Optional[NotificationService] = None,
    ):
        # Dependencies are injected, not created internally
        self.config = config
        self.rotation_service = rotation_service
        self.message_service = message_service
        self.notification_service = notification_service
```

**Benefits:**
- Easy to test (can inject mocks)
- Loosely coupled components
- Easy to swap implementations

### 2. **Strategy Pattern**

Message formatting uses different strategies based on rotation type:

```python
class MessageService:
    def __init__(self, single_group_template: str, split_group_template: str):
        self.single_group_formatter = SingleGroupFormatter(single_group_template)
        self.split_group_formatter = SplitGroupFormatter(split_group_template)

    def format_message(self, rotation: RotationResult) -> str:
        # Select strategy based on rotation type
        if rotation.is_single_group:
            return self.single_group_formatter.format(rotation)
        else:
            return self.split_group_formatter.format(rotation)
```

**Benefits:**
- Easy to add new message formats
- Each formatter has single responsibility
- No conditional logic scattered throughout code

### 3. **Factory Pattern**

Creating notification services uses a factory:

```python
class NotificationServiceFactory:
    @staticmethod
    def create_email_service(...) -> EmailNotificationService:
        return EmailNotificationService(...)

    @staticmethod
    def create_console_service() -> ConsoleNotificationService:
        return ConsoleNotificationService()
```

**Benefits:**
- Centralized creation logic
- Easy to add new notification types (SMS, Slack, etc.)
- Hides implementation details

### 4. **Service Layer Pattern**

Business logic is encapsulated in services:

- `RotationService` - Handles rotation calculations
- `MessageService` - Handles message formatting
- `NotificationService` - Handles sending notifications

**Benefits:**
- Business logic separated from presentation
- Services are reusable
- Easy to test in isolation

### 5. **Configuration Pattern**

Configuration is loaded and validated separately:

```python
@dataclass
class BotConfig:
    email: EmailConfig
    rotation: RotationConfig
    message: MessageConfig

    @classmethod
    def from_yaml(cls, config_path: Path) -> "BotConfig":
        # Load and validate configuration
        ...
```

**Benefits:**
- Type-safe configuration
- Validation in one place
- Easy to extend with new config options

### 6. **Abstract Base Class (ABC)**

`NotificationService` defines an interface:

```python
class NotificationService(ABC):
    @abstractmethod
    def send(self, message: str, subject: Optional[str] = None) -> bool:
        pass
```

Implementations:
- `EmailNotificationService`
- `ConsoleNotificationService`
- (Future: `SMSNotificationService`, `TelegramNotificationService`)

**Benefits:**
- Polymorphism - all notifications work the same way
- Easy to add new notification types
- Interface segregation

---

## Component Responsibilities

### 1. Configuration Layer (`src/config.py`)

**Responsibility:** Load and validate configuration

**Classes:**
- `EmailConfig` - Email settings
- `RotationConfig` - Rotation settings
- `MessageConfig` - Message templates
- `BotConfig` - Complete configuration

**Key Methods:**
- `from_yaml()` - Load from YAML file
- `validate()` - Validate configuration

### 2. Service Layer (`src/services/`)

#### `RotationService`

**Responsibility:** Calculate rotation schedules

**Methods:**
- `calculate_rotation()` - Calculate for current/specific week
- `get_schedule()` - Get multi-week schedule

#### `MessageService`

**Responsibility:** Format messages

**Methods:**
- `format_message()` - Format rotation into message

#### `NotificationService`

**Responsibility:** Send notifications

**Implementations:**
- `EmailNotificationService` - Send via email
- `ConsoleNotificationService` - Print to console

**Methods:**
- `send()` - Send notification

### 3. Application Layer (`src/bot.py`)

#### `RotationBot`

**Responsibility:** Orchestrate the entire process

**Methods:**
- `generate_rotation()` - Get current rotation
- `format_message()` - Format rotation message
- `send_notification()` - Send notification
- `run()` - Execute complete workflow
- `from_config_file()` - Factory method to create bot

### 4. CLI Interface (`src/bot_simple.py`)

**Responsibility:** Provide user-friendly command-line interface

**Functions:**
- `print_rotation_info()` - Display rotation info
- `main()` - CLI entry point

---

## Data Flow

```
1. Load Config
   config.yaml → BotConfig

2. Create Services (Dependency Injection)
   BotConfig → RotationService
   BotConfig → MessageService
   Environment → NotificationService

3. Run Bot
   RotationService.calculate_rotation()
   → RotationResult

   MessageService.format_message(RotationResult)
   → formatted message

   NotificationService.send(message)
   → email sent

4. Display Results
   CLI prints formatted message
```

---

## Extension Points

### Adding a New Notification Type (e.g., SMS)

1. Create new service:
```python
class SMSNotificationService(NotificationService):
    def send(self, message: str, subject: Optional[str] = None) -> bool:
        # Send via SMS API
        pass
```

2. Add factory method:
```python
class NotificationServiceFactory:
    @staticmethod
    def create_sms_service(...) -> SMSNotificationService:
        return SMSNotificationService(...)
```

3. Update `bot_simple.py` to use new service

### Adding a New Message Format

1. Create new formatter:
```python
class CustomFormatter(MessageFormatter):
    def format(self, rotation: RotationResult) -> str:
        # Custom formatting logic
        pass
```

2. Add to `MessageService`:
```python
class MessageService:
    def format_custom(self, rotation: RotationResult) -> str:
        return self.custom_formatter.format(rotation)
```

### Adding a New Config Option

1. Add to dataclass:
```python
@dataclass
class RotationConfig:
    start_date: datetime
    participants: List[str]
    new_option: str  # New field
```

2. Update `from_yaml()` to load new field

3. Update `validate()` to validate new field

---

## Testing Strategy

### Unit Tests

Each service can be tested in isolation:

```python
def test_rotation_service():
    service = RotationService(
        start_date=date(2026, 3, 1),
        participants=["Alice", "Bob", "Charlie", "Diana", "Eve"]
    )
    result = service.calculate_rotation()
    assert result.week_number == 1
    assert len(result.main_group) == 4
```

### Integration Tests

Test bot with mocked services:

```python
def test_bot_run():
    mock_notification = Mock(spec=NotificationService)
    bot = RotationBot(
        config=config,
        rotation_service=rotation_service,
        message_service=message_service,
        notification_service=mock_notification,
    )
    message = bot.run()
    mock_notification.send.assert_called_once()
```

---

## Benefits of This Architecture

✅ **Testability** - Each component can be tested independently

✅ **Maintainability** - Clear separation of concerns, easy to find and fix bugs

✅ **Extensibility** - Easy to add new features (SMS, Telegram, new formatters)

✅ **Flexibility** - Can swap implementations without changing other code

✅ **Scalability** - Can grow from simple script to complex system

✅ **Readability** - Clear structure, easy to understand

✅ **Type Safety** - Using dataclasses and type hints throughout

---

## Key Principles Applied

### SOLID Principles

- **S**ingle Responsibility: Each class has one job
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes can replace base types
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Clean Architecture

- **Independence**: Business logic doesn't depend on frameworks
- **Testability**: Can test without UI, database, or external services
- **Flexibility**: Can swap out external dependencies easily

---

## Future Improvements

1. **Add logging service** - Centralized logging with different levels
2. **Add persistence layer** - Store rotation history
3. **Add scheduling service** - Handle scheduling logic separately
4. **Add metrics/monitoring** - Track success/failure rates
5. **Add retry logic** - Configurable retry strategies
6. **Add caching** - Cache rotation calculations

---

## Summary

This architecture provides:
- Clean separation between layers
- Loosely coupled components
- Easy testing and extension
- Clear data flow
- Type safety

The code is now:
- More maintainable
- More testable
- More scalable
- More professional

All while maintaining the same functionality and simple CLI interface! 🎉
