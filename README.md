# MyBlog
## Описание
  Приложение представляет собой платформу для ведения блогов, где пользователи имеют возможность создавать, редактировать и удалять свои записи, оставлять комментарии к блогам, добавлять категории к своим блогам при желании и искать блоги по названию категорий.
  Реализована гибкая система контроля доступа с использованием RBAC (role-based access control).Система поддерживает роли пользователей, такие как администратор и гость. Гость имеет возможность создавать, редактировать и удалять свои блоги, просматривать блоги других пользователей,писать комментарии и удалять только свои комментарии. Администратор же имеет более расширенные возможности такие как: возможность удалить любой блог и комментарий любого пользователя.


 ## Наименование
 **MyBlog**-это название отражает предназначение самой платформы и основной идеи сервиса: ведение собственного блога.

 ## Предметная область
 Приложение разработано для создания и управления блогами. Оно ориентировано на пользователей, желающих вести личные блоги или управлять тематическими статьями. Система поддерживает администрирование контента и ролей, а также обеспечивает классификацию блогов по категориям для лучшей организации и навигации. Основные сущности системы включают блоги, комментарии, категории и пользователей.

 ## Данные
 ### Пользователь:
 * Имя (обязательное, уникальное)
 * Email (обязательное, уникальное)
 * Пароль (обязательное, захэшированное)
 * Роль (admin, guest, значение по умолчанию - guest)
Для регистрации заполняем все эти данные для создания аккаунта, а для входа в аккаунт нужно сделать авторизацию, где будем указывать наш email и пароль для входа.
После входа в аккаунт мы можем создавать, изменять, смотреть и удалять блоги.
### Блоги:
Для создания блога нам нужно указать:
 * Заголовок блога (обязательное, макс. 255 символов)
 * Содержимое блога (обязательное)
 * Категория блога (опционально)
Для удаления ,изменения и получения определенного блога достаточно ввести id блога.
К созданным блогам можно оставлять комментарии, удалять их и просматривать все комментарии под определенным блогом.
### Комментарии
Для создания комментария достаточно указать:
* id блога
* содержание самого комментария
Для просмотра всех комментариев под блогом нужно указать id блога.
Для удаления комментария нужно указать id комментария.
### Категории
Как было сказано ранее мы можем опционально указывать категории при создании блога, но кроме того мы можем сами дополнять категории и просматривать весь существующий уникальный список.
Имеется возможность поиска блогов по названию категория. Для этого нам нужно ввести название категории из списка категорий и мы получим все блоги, связанные с этим названием.

# Для каждого элемента данных - ограничения:
* Заголовок блога - максимум 255 символов
* Контент блога - минимум 1 символ и максимум 20000
* Название категории - максимум 100 символов
* Электронная почта должна соответствовать формату email
* Содержимое комментария - минимум 1 символ
* Пароль - должен содержать минимум 6 символов, как минимум одну заглавную и прописную букву, иначе выводится: "Password must be at least 6 characters long and contain at least one digit and one uppercase letter."
* Имя пользователя должно быть уникальным, иначе выводится: "The name is taken. Choose the another one."
* email должен быть уникальным и валидным, иначе выводится сообщение: "Email already registered"

# Общие ограничения целостности
* Валидация данных
* Ограничения доступов для различных ролей

# Пользовательские роли
Внутри сервиса две роли:
* Guest: создание блогов, обновление и удаление своих записей, возможность просматривать все блоги, находить блог по id блога, оставлять и удалять комментарии, просматривать комментарии под определенным блогом (по id блога), получать блоги по названию категорий, дополнять список категорий и просматривать его.
* Administrator: имеет более расширенные возможности, так как может удалить блог любого пользователя и удалить любой комментарий.

# API
REST API для управления данными (создание, редактирование, удаление) блогов, комментариев и категорий.
Swagger-документация API проекта находится по пути docs/, где описаны все доступные эндпоинты, возможные запросы, параметры и ответы для каждой операции.

# Технологии разработки
* **FastAPI** — создание API и маршрутизация.
* **SQLAlchemy** — ORM для работы с базой данных.
* **OAuth2** — управление аутентификацией пользователей.
* **Passlib** — хэширование паролей.
* **JWT (JSON Web Tokens)** — управление токенами аутентификации.
* **Docker** - средство контейнеризации и развёртывания приложения

# Язык программировани
* Python 3.12.6

# СУБД
* PostgreSQL
  


 
 





