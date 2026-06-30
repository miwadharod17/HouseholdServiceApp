from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Service(db.Model):
    __tablename__ = 'service'
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    time_required = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professional'
    professional_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    professional_name = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    professional_phone = db.Column(db.String(15), nullable=False, unique=True)
    approval = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False, unique=True)
    location = db.Column(db.String(100), nullable=False)

    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True)

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.professional_id'))
    status = db.Column(db.String(100), nullable=False) #requested, accepted, closed
    visibility = db.Column(db.Integer, nullable=False) #if accepted or closed, visibilty true elseif rejected, false
    request_date = db.Column(db.String(100))

    service = db.relationship('Service', backref='service_requests')
    professional = db.relationship('ServiceProfessional', backref='service_requests')
    rating = db.relationship('Rating', backref='service_request', uselist=False)

class Rating(db.Model):
    __tablename__ = 'ratings'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.request_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)


###############################################################################################################################################

@app.route('/')
def home():
    return render_template('admin_login.html')

#ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form['name']
        admin = Admin.query.filter_by(name=name).first()
        if admin:
            return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_login.html')

#ADMIN DASHBOARD
@app.route('/admin/dashboard/')
def admin_dashboard():

    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    requests = db.session.query(
        ServiceRequest.request_id,
        ServiceProfessional.professional_name,
        Service.service_name,
        Service.description,
        ServiceRequest.status,
        Service.description,
        ServiceProfessional.approval
    ).join(Service, Service.service_id == ServiceRequest.service_id)\
     .join(ServiceProfessional, ServiceProfessional.professional_id == ServiceRequest.professional_id).all()
    
    return render_template('admin_dashboard.html', services=services, professionals=professionals, requests=requests)

#SERVICE DETAILS
@app.route('/service/details/<int:service_id>')
def service_details(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('service_details.html', service=service)

#ADD SERVICE
@app.route('/service/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        description = request.form.get('description')
        time_required = request.form.get('time_required')
        base_price = request.form.get('base_price')

        new_service = Service(
            service_name=service_name,
            description=description,
            time_required=time_required,
            base_price=base_price
        )
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_service.html')

#UPDATE SERVICE
@app.route('/service/update/<int:service_id>', methods=['GET', 'POST'])
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        service.service_name = request.form.get('service_name')
        service.description = request.form.get('description')
        service.time_required = request.form.get('time_required')
        service.base_price = request.form.get('base_price')

        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('update_service.html', service=service)

#DELETE SERVICE
@app.route('/service/delete/<int:service_id>')
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

#PROFESSIONAL DETAILS
@app.route('/professional/details/<int:professional_id>')
def professional_details(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    
    service_requests = db.session.query(
        ServiceRequest.request_id,
        ServiceRequest.customer_id,
        ServiceRequest.status,
        ServiceRequest.visibility,
        Service.service_name,
        Service.description,
        ServiceRequest.professional_id,
        Customer.customer_name,
        Customer.customer_phone,
        Service.base_price,
        Rating.rating
    ).join(Service, ServiceRequest.service_id == Service.service_id) \
     .join(Rating, Rating.request_id == ServiceRequest.request_id) \
     .join(Customer, ServiceRequest.customer_id == Customer.customer_id) \
     .filter(ServiceRequest.professional_id == professional_id).all()

    return render_template(
        'professional_details.html',
        service_professional=professional,
        service_requests=service_requests
    )

#APPROVE PROFESSIONAL
@app.route('/professional/approve/<int:professional_id>')
def approve_professional(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    professional.approval = 1 
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

#REJECT PROFESSIONAL
@app.route('/professional/reject/<int:professional_id>')
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    db.session.delete(professional)  
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

#ADMIN SEARCH
@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    category = request.form.get('category', 'service')
    search_term = request.form.get('search_term', '').lower()
    results = []

    if category == 'service':
        results = ServiceRequest.query.filter(
            (ServiceRequest.status.ilike(f'%{search_term}%'))).all()
    elif category == 'customer':
        results = Customer.query.filter(
            (Customer.customer_name.ilike(f'%{search_term}%'))).all()
    elif category == 'professional':
        results = ServiceProfessional.query.filter(
            (ServiceProfessional.service_name.ilike(f'%{search_term}%'))).all()

    return render_template('admin_search.html', results=results, category=category, search_term=search_term)

#ADMIN SUMMARY
@app.route('/admin/summary')
def admin_summary():
    
    static_folder = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    status_chart_path = os.path.join(static_folder, 'service_requests_status_chart.png')
    ratings_chart_path = os.path.join(static_folder, 'ratings_histogram.png')

    service_requests = ServiceRequest.query.all()
    ratings = Rating.query.all()

    status_data = {}
    ratings_data = []

    if service_requests:
        statuses = [req.status for req in service_requests]
        status_counts = pd.Series(statuses).value_counts()
        status_data = status_counts.to_dict()

        plt.figure(figsize=(8, 6))
        plt.bar(status_counts.index, status_counts.values, color=['blue', 'green', 'pink', 'orange'])
        plt.xlabel('Status')
        plt.ylabel('Count')
        plt.title('Service Request Status Overview')
        plt.savefig(status_chart_path)
        plt.close()
    else:
        status_chart_path = None

    if ratings:
        ratings_data = [rating.rating for rating in ratings]

        plt.figure(figsize=(8, 6))
        plt.hist(ratings_data, bins=range(1, 7))
        plt.xlabel('Rating')
        plt.ylabel('Frequency')
        plt.title('Ratings Distribution')
        plt.xticks(range(1, 6))  
        plt.savefig(ratings_chart_path)
        plt.close()
    else:
        ratings_chart_path = None

    return render_template(
        'admin_summary.html',
        total_requests=len(service_requests),
        status_chart_path=url_for('static', filename='service_requests_status_chart.png') if status_chart_path else None,
        ratings_chart_path=url_for('static', filename='ratings_histogram.png') if ratings_chart_path else None,
        status_data=status_data,
        ratings_data=ratings_data)

###############################################################################################################################################

#PROFESSIONAL LOGIN
@app.route('/professional_login', methods=['GET', 'POST'])
def professional_login():
    if request.method == 'POST':
        login_id = request.form['login_id']  
        professional = ServiceProfessional.query.filter_by(professional_id=login_id).first()

        if professional:
            session['professional_id'] = professional.professional_id
            return redirect(url_for('professional_dashboard', professional_id=login_id))  
        else:
            return redirect(url_for('professional_login'))  
    return render_template('professional_login.html') 

#PROFESSIONAL REGISTER
@app.route('/professional_register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        professional_name = request.form['name']
        professional_phone = request.form['phone']
        service_name = request.form['service_name']
        experience = request.form['experience'] 

        existing_professional = ServiceProfessional.query.filter_by(professional_name=professional_name).first()
        if existing_professional:
            return redirect(url_for('professional_register'))  

        new_professional = ServiceProfessional(
            professional_name=professional_name,
            professional_phone=professional_phone,
            service_name=service_name,
            experience=experience,
            approval=0)

        db.session.add(new_professional)
        db.session.commit()
        return redirect(url_for('professional_login'))  

    return render_template('professional_register.html')  

#PROFESSIONAL DASHBOARD
@app.route('/professional_dashboard/<int:professional_id>')
def professional_dashboard(professional_id):
    professional_id = session.get('professional_id')

    if not professional_id:
        return redirect(url_for('professional_login'))

    professional = ServiceProfessional.query.get_or_404(professional_id)

    open_requests = db.session.query(
    ServiceRequest.request_id,
    Service.service_name,
    Service.description,
    Service.base_price).join(Service).filter(
    ServiceRequest.professional_id == None,
    ServiceRequest.visibility == 1,
    Service.service_name == professional.service_name).all()
    

    closed_requests = db.session.query(
    ServiceRequest,
    Service.service_name,
    Service.description,
    Service.base_price,
    Customer.location,
    Customer.customer_name,
    ServiceRequest.status
    ).join(Service, ServiceRequest.service_id == Service.service_id)\
    .join(Customer, ServiceRequest.customer_id == Customer.customer_id)\
    .filter(
    ServiceRequest.professional_id == professional_id,
    ServiceRequest.status.in_(['closed', 'accepted']),
    ServiceRequest.visibility == 1).all()

    return render_template(
        'professional_dashboard.html',
        professional_id=professional_id,
        professional=professional,
        open_requests=open_requests,
        closed_requests=closed_requests)

#UPDATE REQUEST STATUS
@app.route('/update_request_status', methods=['POST'])
def update_request_status():
    request_id = request.form.get('request_id')
    action = request.form.get('action')

    if not request_id or not action:
        return redirect(url_for('professional_dashboard', professional_id=session.get('professional_id')))

    service_request = ServiceRequest.query.get(request_id)
    professional_id = session.get('professional_id')

    if not service_request:
        return redirect(url_for('professional_dashboard', professional_id=professional_id))

    if professional_id is None:
        return redirect(url_for('login'))

    if action == 'accept':
        service_request.status = 'accepted'
        service_request.visibility = 1
        service_request.professional_id = professional_id

    elif action == 'reject':
        service_request.status = 'rejected'
        service_request.professional_id = professional_id
        service_request.visibility = 0

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('professional_dashboard', professional_id=professional_id))

#PROFESSIONAL SEARCH
@app.route('/professional_search/<int:professional_id>', methods=['GET', 'POST'])
def professional_search(professional_id):
    professional_id = session.get('professional_id')

    if not professional_id:
        return redirect(url_for('professional_login'))

    results = []
    category = request.form.get('category', '')
    search_term = request.form.get('search_term', '')

    if request.method == 'POST' and category == 'location':
        
        results = db.session.query(
            Service.description,
            Customer.customer_id,
            Customer.customer_name,
            Customer.customer_phone,
            Customer.location).join(ServiceRequest, ServiceRequest.customer_id == Customer.customer_id) \
        .join(Service, ServiceRequest.service_id == Service.service_id) \
            .filter(
             ServiceRequest.professional_id == professional_id,  
             Customer.location.ilike(f'%{search_term}%')).all()

    return render_template(
        'professional_search.html',
        professional_id=professional_id,
        results=results,
        category=category,
        search_text=search_term)

#PROFESSIONAL SUMMARY
@app.route('/professional/summary/<int:professional_id>')
def professional_summary(professional_id):
    
    service_requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()

    static_folder = os.path.join(app.root_path, 'static')
    histogram_path = os.path.join(static_folder, f'professional_{professional_id}_histogram.png')
    ratings_chart_path = os.path.join(static_folder, f'professional_{professional_id}_ratings_histogram.png')

    if service_requests:
        statuses = [req.status for req in service_requests]
        status_counts = pd.Series(statuses).value_counts()

        total_requests = len(service_requests)
        closed_requests = status_counts.get('closed', 0)
        assigned_requests = status_counts.get('accepted', 0)

        plt.figure(figsize=(8, 6))
        plt.bar(status_counts.index, status_counts.values, color=['blue', 'green', 'pink'])
        plt.xlabel('Request Status')
        plt.ylabel('Count')
        plt.title(f'Service Requests Summary for Professional {professional_id}')
        plt.savefig(histogram_path)
        plt.clf()

        ratings = Rating.query.join(ServiceRequest).filter(ServiceRequest.professional_id == professional_id).all()

        if ratings:
            ratings_data = [rating.rating for rating in ratings]

            plt.figure(figsize=(8, 6))
            plt.hist(ratings_data, bins=range(1, 7))
            plt.xlabel('Rating')
            plt.ylabel('Frequency')
            plt.title(f'Ratings Distribution for Professional {professional_id}')
            plt.xticks(range(1, 6)) 
            plt.savefig(ratings_chart_path)
            plt.clf()
        else:
            ratings_chart_path = None

        return render_template(
            'professional_summary.html',
            professional_id=professional_id,
            total_requests=total_requests,
            closed_requests=closed_requests,
            assigned_requests=assigned_requests,
            histogram_path=url_for('static', filename=f'professional_{professional_id}_histogram.png'),
            ratings_chart_path=url_for('static', filename=f'professional_{professional_id}_ratings_histogram.png') if ratings_chart_path else None
        )
    else:
        return render_template('professional_summary.html',professional_id=professional_id, message="No service requests found for this professional.")


#PROFESSIONAL PROFILE
@app.route('/professional_profile/<int:professional_id>')
def professional_profile(professional_id):
    professional = ServiceProfessional.query.get_or_404(professional_id)
    return render_template('professional_profile.html', professional_id=professional_id,professional=professional)

############################################################################################################################################

#CUSTOMER LOGIN
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        login_id = request.form['login_id']

        customer = Customer.query.filter_by(customer_id=login_id).first()

        if customer:
            session['customer_id'] = customer.customer_id  
            return redirect(url_for('customer_dashboard', customer_id=login_id))
        else:
            return "Invalid login ID", 403  
    return render_template('customer_login.html')

#CUSTOMER REGISTER
@app.route('/customer_register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        new_customer = Customer(
            customer_name=request.form['customer_name'],
            customer_phone=request.form['customer_phone'],
            location=request.form['location']
        )
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template('customer_register.html')

#CUSTOMER DASHBOARD
@app.route('/customer_dashboard/<int:customer_id>')
def customer_dashboard(customer_id):
    customer_id = session.get('customer_id')

    if not customer_id:
        return redirect(url_for('customer_login'))

    service_requests = db.session.query(
        ServiceRequest.request_id,
        Service.service_name,
        Service.description,
        ServiceRequest.professional_id,
        ServiceRequest.status,
        ServiceRequest.request_date
    ).join(Service, ServiceRequest.service_id == Service.service_id) \
     .filter(ServiceRequest.customer_id == customer_id) \
     .all()

    return render_template(
        'customer_dashboard.html',
        customer_id=customer_id,
        service_requests=service_requests
    )

#UPDATE REQUEST DATE 
@app.route('/request/update/<int:request_id>', methods=['GET', 'POST'])
def update_request(request_id):
    s_request = ServiceRequest.query.get_or_404(request_id)
    customer_id=s_request.customer_id

    if request.method == 'POST':
        s_request.request_date=request.form.get('request_date')

        db.session.commit()
        return redirect(url_for('customer_dashboard', customer_id=customer_id))
    return render_template('update_request.html', request=s_request, customer_id=customer_id)

#CLOSE REQUEST
@app.route('/close_request/<int:request_id>', methods=['GET', 'POST'])
def close_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    customer_id = session.get('customer_id')
    if not customer_id or service_request.customer_id != customer_id:
        return redirect(url_for('customer_dashboard', customer_id=customer_id))

    if request.method == 'POST':
        rating = request.form.get('rating')

        new_rating = Rating(request_id=request_id, rating=rating)
        db.session.add(new_rating)

        service_request.status = 'closed'
        db.session.commit()

        return redirect(url_for('customer_dashboard', customer_id=customer_id))

    return render_template(
        'rating_page.html',
        customer_id=customer_id,
        professional_id=service_request.professional_id,
        request_id=service_request.request_id
    )

#CUSTOMER SEARCH PAGE
@app.route('/customer_search/<int:customer_id>', methods=['GET', 'POST'])
def customer_search(customer_id):
    
    service_names = db.session.query(Service.service_name).distinct().all()
    service_names = [name[0] for name in service_names]
    services = None

    if request.method == 'POST':
        service_name = request.form.get('service_name')
        base_price = request.form.get('base_price')
        query = Service.query

        if service_name:
            query = query.filter(Service.service_name == service_name)
        if base_price:
            query = query.filter(Service.base_price <= int(base_price))

        services = query.all()

    return render_template(
        'customer_search.html',
        customer_id=customer_id,
        service_names=service_names,
        services=services
    )

#ADD DATE OF REQUEST
@app.route('/select_booking_date/<int:service_id>', methods=['GET', 'POST'])
def select_booking_date(service_id):
    customer_id = session.get('customer_id')

    if not customer_id:
        return redirect(url_for('customer_login'))

    if request.method == 'POST':
        request_date = request.form.get('request_date')

        new_request = ServiceRequest(
            customer_id=customer_id,
            service_id=service_id,
            professional_id=None,
            status='requested',
            visibility=1,
            request_date=request_date  
        )

        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('customer_dashboard', customer_id=customer_id))

    return render_template('select_booking_date.html', service_id=service_id, customer_id=customer_id)

#CUSTOMER SUMMARY
@app.route('/customer/summary/<int:customer_id>')
def customer_summary(customer_id):
    service_requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()

    static_folder = os.path.join(app.root_path, 'static')
    histogram_path = os.path.join(static_folder, f'professional_{customer_id}_histogram.png')

    if service_requests:
        statuses = [req.status for req in service_requests]
        status_counts = pd.Series(statuses).value_counts()

        total_requests = len(service_requests)
        closed_requests = status_counts.get('closed', 0)
        assigned_requests = status_counts.get('accepted', 0)
        requested_requests = status_counts.get('requested', 0)

        plt.figure(figsize=(8, 6))
        plt.bar(status_counts.index, status_counts.values, color=['blue', 'green', 'pink'])
        plt.xlabel('Request Status')
        plt.ylabel('Count')
        plt.title(f'Service Requests Summary for Professional {customer_id}')
        plt.savefig(histogram_path)
        plt.clf()

        return render_template(
            'customer_summary.html',
            customer_id=customer_id,
            total_requests=total_requests,
            closed_requests=closed_requests,
            assigned_requests=assigned_requests,
            requested_requests=requested_requests,
            histogram_path=url_for('static', filename=f'professional_{customer_id}_histogram.png')
        )
    else:
        return render_template('customer_summary.html',customer_id=customer_id, message="No service requests found for this professional.")


#CUSTOMER PROFILE
@app.route('/customer_profile/<int:customer_id>')
def customer_profile(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customer_profile.html', customer_id=customer_id,customer=customer)

###############################################################################################################################################

@app.route('/admin_logout')
def admin_logout():
    if 'admin_id' in session:
        session.pop('admin_id', None)  
    return redirect(url_for('admin_login'))  

@app.route('/customer_logout')
def customer_logout():
    if 'customer_id' in session:
        session.pop('customer_id', None)  
    return redirect(url_for('customer_login'))  

@app.route('/service_professional_logout')
def service_professional_logout():
    if 'service_professional_id' in session:
        session.pop('service_professional_id', None)  
    return redirect(url_for('service_professional_login'))  


if __name__ == '__main__':
    app.run(debug=True)