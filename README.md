# Household Services Management System

A full-stack web application that connects **customers** with **service professionals** for household services. The platform supports **Role-Based Access Control (RBAC)** with dedicated dashboards for administrators, customers, and service professionals, enabling end-to-end service management, booking, approvals, analytics, and reporting.

---

## Features

### Admin
- Create, update, and delete services
- View service details
- Approve or reject service professional registrations
- View customer and professional details
- Monitor all service requests
- Search customers, professionals, and service requests
- View analytics dashboards
- Export reports as CSV files

### Customer
- Register and log in
- Browse available services
- Book multiple household services
- Track service request history
- Close completed requests
- Rate completed services
- View request analytics dashboard
- Manage profile information

### Service Professional
- Register and await admin approval
- View new customer requests
- Accept or reject service requests
- Manage accepted and completed requests
- Search assigned customers
- View ratings and request analytics
- Manage profile information

---

## Tech Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy

### Frontend
- HTML
- Jinja2
- CSS

### Database
- SQLite

### Data Processing & Visualization
- Pandas
- Matplotlib

---

## System Architecture

```
                 +----------------+
                 |     Admin      |
                 +----------------+
                    /    |     \
                   /     |      \
          Services   Professionals  Requests
                 \      |      /
                  \     |     /
               +------------------+
               |     Database     |
               +------------------+
                 /             \
                /               \
      +----------------+   +----------------------+
      |   Customers    |   | Service Professionals|
      +----------------+   +----------------------+
```

---

## Database Schema

### Admin
| Field | Description |
|-------|-------------|
| id | Admin ID |
| name | Admin Name |

### Service
| Field | Description |
|-------|-------------|
| service_id | Primary Key |
| service_name | Name of service |
| description | Service description |
| time_required | Estimated completion time |
| base_price | Base service cost |

### Service Professional
| Field | Description |
|-------|-------------|
| professional_id | Primary Key |
| professional_name | Professional name |
| service_name | Associated service |
| experience | Years of experience |
| professional_phone | Contact number |
| approval | Approval status |

### Customer
| Field | Description |
|-------|-------------|
| customer_id | Primary Key |
| customer_name | Customer name |
| customer_phone | Contact number |
| location | Customer location |

### Service Request
| Field | Description |
|-------|-------------|
| request_id | Primary Key |
| customer_id | Foreign Key |
| service_id | Foreign Key |
| professional_id | Foreign Key |
| status | Request status |
| visibility | Request visibility |

### Ratings
| Field | Description |
|-------|-------------|
| rating_id | Primary Key |
| request_id | Foreign Key |
| rating | Customer rating |

---

## Entity Relationships

- Admin → Service (One-to-Many)
- Customer → Service (Many-to-Many)
- Customer → Service Request (One-to-Many)
- Service → Service Request (One-to-Many)
- Service Professional → Service (Many-to-One)
- Service Professional → Service Request (One-to-Many)
- Service Request → Ratings (One-to-One)

---

## Project Structure

```
Household-Services/
│
├── app.py
├── models.py
├── routes/
├── templates/
│   ├── admin/
│   ├── customer/
│   ├── professional/
│   └── base.html
├── static/
│   ├── css/
│   ├── images/
│   └── charts/
├── database/
├── exports/
├── requirements.txt
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/household-services.git
cd household-services
```

### Create a virtual environment

```bash
python -m venv venv
```

Activate the environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python new.py
```

Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## Key Functionalities

- Secure authentication
- Role-Based Access Control (RBAC)
- Multi-user dashboards
- Service booking workflow
- Professional approval workflow
- CRUD operations
- Search and filtering
- Ratings system
- Analytics dashboards
- CSV export

---

## Future Enhancements

- Email notifications
- Payment gateway integration
- Real-time service tracking
- Image uploads for professionals
- REST API support
- Docker deployment
- Unit and integration testing

---

## Learning Outcomes

This project demonstrates experience with:

- Flask web development
- SQLAlchemy ORM
- Relational database design
- Authentication and authorization
- Role-Based Access Control (RBAC)
- CRUD application development
- Data visualization using Matplotlib
- Search and reporting
- Multi-user workflow management
