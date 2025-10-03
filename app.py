import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'f62164cbb144fe8396e3bf51742cba41e82e7fa235394e50ff5166e292e994c6'

# Upload configuration
UPLOAD_FOLDER = "static/gallery"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory data storage
data_store = {
    'appointments': [],
    'contact_messages': [],
    'gallery': []
}

# Helper functions
def get_next_id(table):
    """Get next auto-increment ID for a table"""
    if not data_store[table]:
        return 1
    return max(item['id'] for item in data_store[table]) + 1

# Blog and service data
blogs_data = {
    "puppy_proofing": {
        "id": "puppy_proofing",
        "title": "10 Essential Puppy Proofing Tips from SKvets",
        "image": "images/puppy.jpeg",
        "excerpt": "Create a safe and friendly environment for your new best friend...",
        "file": "blogs/puppy_proofing.html"
    },
    "puppy_care": {
        "id": "puppy_care",
        "title": "How to take care of your Puppy and feed them?",
        "image": "images/Maltese Dog 1.png",
        "excerpt": "The first week of the puppies' lives is the most critical to their survival...",
        "file": "blogs/puppy_care.html"
    },
    "vet_checkups": {
        "id": "vet_checkups",
        "title": "Why Regular Veterinary Checkups are Important",
        "image": "images/img2.jpg",
        "excerpt": "Routine vet visits ensure your pet's long-term health and well-being...",
        "file": "blogs/vet_checkups.html"
    },
    "pet_nutrition": {
        "id": "pet_nutrition",
        "title": "The Ultimate Pet Nutrition Guide",
        "image": "images/img4.jpg",
        "excerpt": "Learn how to provide a balanced diet for your pet to keep them healthy...",
        "file": "blogs/pet_nutrition.html"
    },
    "dog_training": {
        "id": "dog_training",
        "title": "Top 5 Dog Training Tips for Beginners",
        "image": "images/img5.jpg",
        "excerpt": "Training your dog doesn't have to be stressful. Follow these expert tips...",
        "file": "blogs/dog_training.html"
    },
    "cat_care": {
        "id": "cat_care",
        "title": "Essential Tips for Keeping Your Cat Happy",
        "image": "images/img10.jpg",
        "excerpt": "Cats require specific care and attention. Learn the best ways to care for them...",
        "file": "blogs/cat_care.html"
    },
    "senior_pet_care": {
        "id": "senior_pet_care",
        "title": "Caring for Senior Pets: What You Need to Know",
        "image": "images/img6.jpg",
        "excerpt": "Older pets need special care. Here are tips to keep them comfortable...",
        "file": "blogs/senior_pet_care.html"
    },
    "dog_breeds": {
        "id": "dog_breeds",
        "title": "Choosing the Right Dog Breed for Your Lifestyle",
        "image": "images/img8.jpg",
        "excerpt": "Discover which dog breed suits your lifestyle the best...",
        "file": "blogs/dog_breeds.html"
    },
    "pet_emergencies": {
        "id": "pet_emergencies",
        "title": "How to Handle Pet Emergencies",
        "image": "images/img11.jpg",
        "excerpt": "Knowing how to act in an emergency can save your pet's life...",
        "file": "blogs/pet_emergencies.html"
    }
}

services_data = {
    "vaccination": {
        "title": "Pet Vaccination Services",
        "image": "imgs1.png",
        "description": "Comprehensive vaccination services for your pets at home",
        "file": "services/vaccination.html"
    },
    "general_treatment": {
        "title": "General Pet Treatment",
        "image": "imgs2.jpg",
        "description": "Comprehensive general treatment services for all your pet's health needs",
        "file": "services/general_treatment.html"
    },
    "deworming": {
        "title": "Pet Deworming Services",
        "image": "imgs3.jpg",
        "description": "Professional deworming services with fecal analysis",
        "file": "services/deworming.html"
    },
    "grooming": {
        "title": "Pet Grooming Services",
        "image": "imgs4.jpg",
        "description": "Professional grooming services in the comfort of your home",
        "file": "services/grooming.html"
    },
    "nail_trimming": {
        "title": "Professional Nail Trimming",
        "image": "nail.jpeg",
        "description": "Expert nail care to keep your pet comfortable and healthy",
        "file": "services/nail_trimming.html"
    },
    "dental_care": {
        "title": "Pet Dental Care",
        "image": "imgs6.jpg",
        "description": "Comprehensive dental health services for your pet",
        "file": "services/dental_care.html"
    },
    "pet_xray": {
        "title": "Mobile Pet X-Ray Services",
        "image": "imgs7.jpg",
        "description": "Advanced diagnostic imaging at your doorstep",
        "file": "services/pet_xray.html"
    },
    "emergency_care": {
        "title": "24/7 Emergency Pet Care",
        "image": "imgs8.jpg",
        "description": "Immediate veterinary response for urgent situations",
        "file": "services/emergency_care.html"
    },
    "nutrition_guidance": {
        "title": "Pet Nutrition Consultation",
        "image": "imgs9.jpg",
        "description": "Personalized nutrition plans for optimal pet health",
        "file": "services/nutrition_guidance.html"
    }
}

# ===========================================
# PUBLIC ROUTES
# ===========================================

@app.route('/')
def index():
    services = []
    for service_id, data in services_data.items():
        services.append({
            "title": data["title"],
            "description": data["description"],
            "image": data["image"],
            "link": url_for('service_detail', service_id=service_id)
        })
    return render_template('index.html', services=services)

@app.route('/contact_form_submit', methods=['POST'])
def contact_form_submit():
    """Handle contact form submission from homepage"""
    if request.method == 'POST':
        name = request.form.get('full_name', '') or request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        # Check which action was selected
        action = request.form.get('action', 'database')
        
        if action == 'whatsapp':
            # Format WhatsApp message
            whatsapp_message = f"*Contact Form Submission*%0A%0A"
            whatsapp_message += f"*Name:* {name}%0A"
            whatsapp_message += f"*Email:* {email}%0A"
            whatsapp_message += f"*Subject:* {subject}%0A"
            whatsapp_message += f"*Message:* {message}"
            
            # Replace with your WhatsApp number (with country code, no + or -)
            whatsapp_number = "919876543210"  # Example: 919876543210 for India
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"
            
            return redirect(whatsapp_url)
        else:
            # Save to database
            data_store['contact_messages'].append({
                'id': get_next_id('contact_messages'),
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'status': 'unread',
                'created_at': datetime.now()
            })
            
            flash('Message sent successfully! We will get back to you soon.', 'success')
            return redirect(url_for('index') + '#contact')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        # Check which action was selected
        action = request.form.get('action', 'database')
        
        if action == 'whatsapp':
            # Format WhatsApp message for appointment
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            pet_name = request.form.get('pet_name', '')
            service = request.form.get('service', '')
            preferred_date = request.form.get('preferred_date', '')
            preferred_time = request.form.get('preferred_time', '')
            message = request.form.get('message', '')
            
            whatsapp_message = f"*Appointment Request*%0A%0A"
            whatsapp_message += f"*Name:* {name}%0A"
            whatsapp_message += f"*Email:* {email}%0A"
            whatsapp_message += f"*Phone:* {phone}%0A"
            if pet_name:
                whatsapp_message += f"*Pet Name:* {pet_name}%0A"
            if service:
                whatsapp_message += f"*Service:* {service}%0A"
            if preferred_date:
                whatsapp_message += f"*Preferred Date:* {preferred_date}%0A"
            if preferred_time:
                whatsapp_message += f"*Preferred Time:* {preferred_time}%0A"
            if message:
                whatsapp_message += f"*Message:* {message}"
            
            # Replace with your WhatsApp number (with country code, no + or -)
            whatsapp_number = "8208657969"  # Example: 919876543210 for India
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"
            
            return redirect(whatsapp_url)
        else:
            # Save to database
            data_store['appointments'].append({
                'id': get_next_id('appointments'),
                'name': request.form['name'],
                'email': request.form['email'],
                'phone': request.form['phone'],
                'pet_name': request.form.get('pet_name', ''),
                'service': request.form.get('service', ''),
                'preferred_date': request.form.get('preferred_date'),
                'preferred_time': request.form.get('preferred_time'),
                'message': request.form.get('message', ''),
                'status': 'pending',
                'created_at': datetime.now()
            })
            
            flash('Appointment request submitted successfully! We will contact you soon.', 'success')
            return redirect(url_for('appointment'))
    
    return render_template('appointment.html')

@app.route("/gallery")
def gallery():
    images = sorted(data_store['gallery'], key=lambda x: x['uploaded_at'], reverse=True)
    return render_template("gallery.html", images=images)

@app.route('/blogs')
def blogs():
    return render_template('blogs.html', blogs=blogs_data)

@app.route('/blog/<blog_id>')
def blog_detail(blog_id):
    blog = blogs_data.get(blog_id)
    if not blog:
        abort(404)
    return render_template(blog["file"], blog=blog)

@app.route('/services')
def services():
    return render_template('services.html', services=services_data)

@app.route('/service/<service_id>')
def service_detail(service_id):
    service = services_data.get(service_id)
    if not service:
        abort(404)
    return render_template(service["file"], service=service)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name') or request.form.get('full_name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        # Check which action was selected
        action = request.form.get('action', 'database')
        
        if action == 'whatsapp':
            # Format WhatsApp message
            whatsapp_message = f"*Contact Form Submission*%0A%0A"
            whatsapp_message += f"*Name:* {name}%0A"
            whatsapp_message += f"*Email:* {email}%0A"
            whatsapp_message += f"*Subject:* {subject}%0A"
            whatsapp_message += f"*Message:* {message}"
            
            # Replace with your WhatsApp number (with country code, no + or -)
            whatsapp_number = "8208657969"  # Example: 919876543210 for India
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message}"
            
            return redirect(whatsapp_url)
        else:
            # Save to database
            data_store['contact_messages'].append({
                'id': get_next_id('contact_messages'),
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'status': 'unread',
                'created_at': datetime.now()
            })
            
            flash('Message sent successfully! We will get back to you soon.', 'success')
            
            # Redirect based on form source
            if request.form.get('full_name'):
                return redirect(url_for('index') + '#contact')
            else:
                return redirect(url_for('contact'))
    
    return render_template('contact.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port, debug=True)
