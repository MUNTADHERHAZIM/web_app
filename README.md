# موقع المقالات

موقع ويب مبني بـ Django لنشر وإدارة المقالات مع واجهة مستخدم عربية.

## المميزات

- نظام إدارة المقالات مع دعم للمؤلفين والتصنيفات
- نظام تعليقات متكامل
- نظام بحث متقدم
- إمكانية تحويل المقالات إلى PDF
- نظام اشتراك في النشرة البريدية
- تتبع تفاعلات المستخدمين وتحليلات القراءة
- واجهة مستخدم عربية جذابة وسهلة الاستخدام

## المتطلبات

- Python 3.8+
- PostgreSQL
- pip

## التثبيت

1. قم بإنشاء قاعدة بيانات PostgreSQL:
```sql
CREATE DATABASE myappdb;
```

2. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

3. قم بتهيئة قاعدة البيانات:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. قم بإنشاء مستخدم مدير:
```bash
python manage.py createsuperuser
```

5. قم بتشغيل الخادم:
```bash
python manage.py runserver
```

## الاستخدام

1. قم بزيارة `http://localhost:8000/admin` لإدارة المحتوى
2. قم بإضافة بعض التصنيفات والمؤلفين والمقالات
3. قم بزيارة `http://localhost:8000` لعرض الموقع

## الهيكل

```
myapp/
├── models.py        # نماذج البيانات
├── views.py         # المعالجات
├── urls.py          # توجيهات URL
├── admin.py         # تكوين لوحة الإدارة
└── templates/       # قوالب HTML
    └── myapp/
        ├── base.html
        ├── home.html
        ├── article_detail.html
        └── search_results.html
```

## المساهمة

نرحب بمساهماتكم! يرجى إرسال pull request أو فتح issue لأي اقتراحات أو تحسينات.
