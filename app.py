from flask import Flask, render_template, request, redirect, url_for, flash
import os
import csv
from datetime import datetime
import joblib
import webbrowser
from threading import Timer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

INVOICE_FOLDER = "invoices"
SALES_CSV = "sales.csv"

# Email Configuration
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.gmail.com',
#     'smtp_port': 587,
#     'email': 'your-email@gmail.com',  # Replace with your email
#     'password': 'your-app-password',   # Replace with your app password
#     'sender_name': 'Amazon India'
# }

if not os.path.exists(INVOICE_FOLDER):
    os.makedirs(INVOICE_FOLDER)

# def send_email_receipt(customer_email, customer_name, order_no, receipt_file_path):
#     """Send email receipt to customer"""
#     try:
#         # Create message
#         msg = MIMEMultipart()
#         msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['email']}>"
#         msg['To'] = customer_email
#         msg['Subject'] = f"Your Amazon Order Receipt - #{order_no:04d}"
        
#         # Email body
#         body = f"""
#         Dear {customer_name},
        
#         Thank you for your order with Amazon!
        
#         Your order #{order_no:04d} has been successfully processed and your receipt is attached.
        
#         Order Details:
#         - Order Number: #{order_no:04d}
#         - Date: {datetime.now().strftime("%d-%m-%Y %H:%M")}
        
#         You can track your order status in your Amazon account.
        
#         If you have any questions, please contact our customer service:
#         📞 1800-3000-9009
#         📧 customer-service@amazon.in
        
#         Thank you for shopping with Amazon!
        
#         Best regards,
#         Amazon Customer Service Team
#         """
        
#         msg.attach(MIMEText(body, 'plain'))
        
#         # Attach receipt file
#         if os.path.exists(receipt_file_path):
#             with open(receipt_file_path, "rb") as attachment:
#                 part = MIMEBase('application', 'octet-stream')
#                 part.set_payload(attachment.read())
#                 encoders.encode_base64(part)
#                 part.add_header(
#                     'Content-Disposition',
#                     f'attachment; filename= "Amazon_Receipt_{order_no:04d}.txt"'
#                 )
#                 msg.attach(part)
        
#         # Send email
#         server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
#         server.starttls()
#         server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
#         text = msg.as_string()
#         server.sendmail(EMAIL_CONFIG['email'], customer_email, text)
#         server.quit()
        
#         return True, "Email sent successfully!"
        
#     except Exception as e:
#         return False, f"Failed to send email: {str(e)}"

def analyze_sentiment_detailed(feedback):
    """Enhanced sentiment analysis with confidence and details"""
    if not feedback or not feedback.strip():
        return None, None, None
    
    # Get prediction and probability
    X = vectorizer.transform([feedback])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0]
    
    # Determine sentiment and confidence
    sentiment = "Positive" if pred == 1 else "Negative"
    confidence = max(prob) * 100
    
    # Word count for analysis
    word_count = len(feedback.split())
    
    return sentiment, confidence, word_count

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return redirect('/')

    # Simulate processing time for loading spinner
    time.sleep(2)

    # Get form data
    items = []
    names = request.form.getlist('item_name')
    qtys = request.form.getlist('item_qty')
    prices = request.form.getlist('item_price')
    feedback = request.form.get('feedback')

    # Get customer details
    customer_name = request.form.get('customer_name')
    customer_address = request.form.get('customer_address')
    customer_phone = request.form.get('customer_phone')
    customer_email = request.form.get('customer_email')
    order_date = request.form.get('order_date')
    delivery_date = request.form.get('delivery_date')
    payment_method = request.form.get('payment_method')

    # Process items
    for name, qty, price in zip(names, qtys, prices):
        if name.strip() == "" or qty == "" or price == "":
            continue
        items.append((name.strip(), int(qty), float(price)))

    if not items:
        flash("No valid items provided. Please go back and enter at least one item.", "error")
        return redirect('/')

    # Calculate totals
    subtotal = sum(q * p for _, q, p in items)
    gst = subtotal * 0.18
    
    # Conditional shipping charges logic
    if subtotal < 50:
        shipping = 40.0
        shipping_text = "₹40.00"
    elif subtotal >= 500:
        shipping = 0.0
        shipping_text = "FREE (₹500+ order)"
    else:
        shipping = 20.0
        shipping_text = "₹20.00"
    
    total = subtotal + gst + shipping

    # Enhanced sentiment analysis
    sentiment, confidence, word_count = analyze_sentiment_detailed(feedback)

    # Generate order number
    order_no = len(os.listdir(INVOICE_FOLDER)) + 1
    order_file = os.path.join(INVOICE_FOLDER, f"order_{order_no:04d}.txt")
    date_str = datetime.now().strftime("%d-%m-%Y %H:%M")

    # Save enhanced receipt to file
    with open(order_file, "w", encoding='utf-8') as f:
        f.write("           AMAZON ORDER RECEIPT\n")
        f.write(f"Order No: #{order_no:04d}\n")
        f.write(f"Generated: {date_str}\n")
        f.write("-" * 40 + "\n")
        f.write("CUSTOMER DETAILS:\n")
        f.write(f"Name: {customer_name}\n")
        f.write(f"Phone: {customer_phone}\n")
        f.write(f"Email: {customer_email if customer_email else 'Not provided'}\n")
        f.write(f"Address: {customer_address}\n")
        f.write("-" * 40 + "\n")
        f.write("ORDER DETAILS:\n")
        f.write(f"Order Date: {order_date}\n")
        f.write(f"Delivery Date: {delivery_date}\n")
        f.write(f"Payment Method: {payment_method}\n")
        f.write("-" * 40 + "\n")
        f.write("ITEMS ORDERED:\n")
        
        for i, (name, qty, price) in enumerate(items, 1):
            item_total = qty * price
            f.write(f"{i}. {name}\n")
            f.write(f"   Qty: {qty} x ₹{price:.2f} = ₹{item_total:.2f}\n")
            f.write("\n")
        
        f.write("-" * 40 + "\n")
        f.write("PAYMENT SUMMARY:\n")
        f.write(f"Subtotal:        ₹{subtotal:>10.2f}\n")
        f.write(f"GST (18%):       ₹{gst:>10.2f}\n")
        f.write(f"Shipping:        {shipping_text:>15}\n")
        f.write("-" * 30 + "\n")
        f.write(f"TOTAL:           ₹{total:>10.2f}\n")
        
        # Shipping policy info
        f.write("-" * 40 + "\n")
        f.write("SHIPPING POLICY:\n")
        f.write("• Orders < ₹50: ₹40 shipping charge\n")
        f.write("• Orders ₹50-₹499: ₹20 shipping charge\n")
        f.write("• Orders ₹500+: FREE shipping\n")
        
        # Enhanced feedback section
        if feedback and feedback.strip():
            f.write("-" * 40 + "\n")
            f.write("CUSTOMER FEEDBACK:\n")
            f.write(f'"{feedback}"\n\n')
            
            if sentiment == "Positive":
                f.write("Rating: ★★★★★ (Positive Experience)\n")
                f.write("Status: 😊 Customer Satisfied\n")
                f.write(f"AI Confidence: {confidence:.1f}%\n")
            else:
                f.write("Rating: ★★☆☆☆ (Needs Improvement)\n")
                f.write("Status: 😞 Customer Dissatisfied\n")
                f.write(f"AI Confidence: {confidence:.1f}%\n")
            
            f.write(f"Words Analyzed: {word_count}\n")
        
        f.write("-" * 40 + "\n")
        f.write("Thank you for shopping with Amazon!\n")
        f.write("Customer Service: 1800-3000-9009\n")
        f.write("Email: customer-service@amazon.in\n")
        f.write("=" * 40 + "\n")

    # Send email if customer email provided
    email_sent = False
    email_message = ""
    if customer_email and customer_email.strip():
        email_sent, email_message = send_email_receipt(
            customer_email, customer_name, order_no, order_file
        )

    # Save to CSV
    with open(SALES_CSV, "a", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if os.stat(SALES_CSV).st_size == 0:
            writer.writerow(["Order No", "Date", "Customer Name", "Email", "Address", "Phone", 
                           "Order Date", "Delivery Date", "Payment Method", 
                           "Subtotal", "GST", "Shipping", "Total", "Feedback", "Sentiment", 
                           "Confidence", "Word Count", "Email Sent"])
        
        writer.writerow([order_no, date_str, customer_name, customer_email, customer_address, customer_phone,
                        order_date, delivery_date, payment_method, 
                        subtotal, gst, shipping, total, feedback, sentiment, 
                        confidence if confidence else "", word_count if word_count else "", email_sent])

    # Flash success message
    flash(f"Order #{order_no:04d} generated successfully!", "success")
    if email_sent:
        flash(f"Receipt sent to {customer_email}", "success")
    elif customer_email:
        flash(f"Failed to send email: {email_message}", "error")

    # Render invoice template
    return render_template('invoice.html', 
                          order_no=order_no, 
                          date=date_str,
                          customer_name=customer_name,
                          customer_address=customer_address,
                          customer_phone=customer_phone,
                          customer_email=customer_email,
                          order_date=order_date,
                          delivery_date=delivery_date,
                          payment_method=payment_method,
                          items=items, 
                          subtotal=subtotal, 
                          gst=gst,
                          shipping=shipping,
                          shipping_text=shipping_text,
                          total=total, 
                          feedback=feedback, 
                          sentiment=sentiment,
                          email_sent=email_sent,
                          email_message=email_message)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)
