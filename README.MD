
# AdStart

## Описание

AdStart - это платформа для управления партнёрскими программами, включающая регистрацию рекламодателей и вебмастеров, а также управление партнёрами, офферами и сайтами.

## Схема Базы данных

### 1. Административные пользователи (AdminUser)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | email                       | EmailField (unique)         |
|    | role                        | CharField                   |
|    | telegram                    | CharField (blank=True)      |
|    | phone                       | CharField (blank=True)      |
+----+-----------------------------+-----------------------------+
```

### 2. Рекламодатель (Advertiser)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | email                       | EmailField (unique)         |
|    | telegram                    | CharField (blank=True)      |
|    | phone                       | CharField (blank=True)      |
+----+-----------------------------+-----------------------------+
```

### 3. Вебмастер (Webmaster)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | email                       | EmailField (unique)         |
|    | telegram                    | CharField (blank=True)      |
|    | phone                       | CharField (blank=True)      |
|    | experience                  | TextField (blank=True)      |
|    | stats_screenshot            | ImageField (blank=True)     |
+----+-----------------------------+-----------------------------+
```

### 4. Категория (Category)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | name                        | CharField                   |
|    | is_private                  | BooleanField                |
+----+-----------------------------+-----------------------------+
```

### 5. Партнер (Partner)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
| FK | admin_user_id               | ForeignKey(AdminUser)       |
| FK | advertiser_user_id          | ForeignKey(Advertiser)      |
|    | logo                        | ImageField                  |
|    | name                        | CharField                   |
|    | legal_name                  | CharField                   |
|    | license                     | FileField                   |
|    | official_website            | URLField                    |
|    | legal_address               | TextField                   |
|    | actual_address              | TextField                   |
|    | company_details             | TextField                   |
|    | phone                       | CharField                   |
|    | deposit                     | DecimalField                |
+----+-----------------------------+-----------------------------+
```

### 6. Оффер (Offer)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
| FK | partner_id                  | ForeignKey(Partner)         |
|    | status                      | CharField                   |
|    | logo                        | ImageField                  |
|    | name                        | CharField                   |
|    | legal_name                  | CharField                   |
|    | inn                         | CharField                   |
|    | contract_number             | CharField                   |
|    | contract_date               | DateField                   |
|    | license                     | FileField                   |
|    | official_website            | URLField                    |
|    | legal_address               | TextField                   |
|    | actual_address              | TextField                   |
|    | working_hours               | CharField                   |
|    | description                 | TextField                   |
|    | geo                         | CharField                   |
|    | lead_validity               | CharField                   |
|    | landing_page_url            | URLField                    |
|    | post_request_docs           | TextField                   |
|    | lead_price                  | DecimalField                |
+----+-----------------------------+-----------------------------+
```

### 7. Сайт (Site)

```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
| FK | offer_id                    | ForeignKey(Offer)           |
|    | name                        | CharField                   |
|    | archive                     | FileField                   |
|    | landing_type                | CharField                   |
|    | status                      | CharField                   |
|    | path                        | CharField                   |
| FK | webmaster_id                | ForeignKey(Webmaster)       |
+----+-----------------------------+-----------------------------+
```

## Регистрация и Подтверждение

### Регистрация

#### Запрос кода подтверждения
**Endpoint:** `POST /accounts/api/request-confirmation-code/`

**Parameters:**
- `email` (string): Email для регистрации.

**Response:**
- `message` (string): Сообщение о результате запроса.

#### Подтверждение email и регистрация
**Endpoint:** `POST /accounts/api/confirm-email/`

**Parameters:**
- `email` (string): Email для подтверждения.
- `confirmation_code` (string): Код подтверждения, полученный по email.
- `user_type` (string): Тип пользователя ('advertiser' или 'webmaster').
- `password` (string): Пароль для учетной записи.
- Дополнительные параметры зависят от типа пользователя:
  - `advertiser`: `telegram`, `phone`
  - `webmaster`: `telegram`, `phone`, `experience`, `stats_screenshot`

**Response:**
- `message` (string): Сообщение о результате подтверждения и регистрации.
