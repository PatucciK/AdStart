
# Схема Базы данных для проекта AdStart

## 1. Административные пользователи (AdminUser)
```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | email                       | EmailField (unique)         |
|    | role                        | CharField                   |
|    | telegram                    | CharField (blank=True)      |
|    | phone                       | CharField (blank=True)      |
+----+-----------------------------+-----------------------------+
```

**Описание:**
- Хранит информацию о административных пользователях, включая email, роль (админ, финансы, менеджер, верстальщик, оператор колл-центра), телеграм и телефон.

## 2. Рекламодатель (Advertiser)
```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | email                       | EmailField (unique)         |
|    | telegram                    | CharField (blank=True)      |
|    | phone                       | CharField (blank=True)      |
+----+-----------------------------+-----------------------------+
```

**Описание:**
- Хранит информацию о рекламодателях, включая email, телеграм и телефон.

## 3. Вебмастер (Webmaster)
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

**Описание:**
- Хранит информацию о вебмастерах, включая email, телеграм, телефон, опыт и скриншот статистики.

## 4. Категория (Category)
```
+----+-----------------------------+-----------------------------+
| PK | id                          | Integer (AutoField)         |
|    | name                        | CharField                   |
|    | is_private                  | BooleanField                |
+----+-----------------------------+-----------------------------+
```

**Описание:**
- Хранит категории партнеров с названием и флагом приватности.

## 5. Партнер (Partner)
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

**Описание:**
- Хранит информацию о партнерах, включая администратора и рекламодателя, логотип, название, юридическое название, лицензию, официальный сайт, адреса, реквизиты компании и депозит.

## 6. Оффер (Offer)
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

**Описание:**
- Хранит информацию об офферах, включая статус, логотип, название, юридическое название, ИНН, номер и дату договора, лицензию, официальный сайт, юридический и фактический адреса, режим работы, описание, ГЕО, валидность лида, ссылку на посадочную страницу, документацию по постзапросам и цену за лид.

## 7. Сайт (Site)
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

**Описание:**
- Хранит информацию о сайтах, прикрепленных к офферам, включая название, архив, тип посадки, статус, путь и вебмастера.
