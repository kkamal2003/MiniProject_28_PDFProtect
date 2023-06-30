from django.shortcuts import render,redirect

from django.http import HttpResponse
from django.core.files.storage import default_storage
import random,uuid,os,PyPDF2
from django.contrib import messages
from django.conf import settings
from django.core.mail  import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def index(request):
  
   if request.method == 'POST':
      print("HELLO")
      file = request.FILES['formFile']
      password = request.POST['password']
      email = request.POST['email']
      
      unique_filename = str(uuid.uuid4()) + '_' + file.name

      file_path=default_storage.save('PDFfiles/' + unique_filename, file)

      
      
      absolute_file_path = os.path.join(default_storage.location, file_path)
      print(default_storage.location)
      print(file_path)
      print(absolute_file_path)
      

      with open(absolute_file_path, 'rb') as file_obj:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            pdf_writer.encrypt(password)
            
            
           # Create a new file path for the processed file
            processed_file_path = os.path.join(default_storage.location,'Protected', unique_filename + '.processed.pdf')
            print(processed_file_path)

             # Save the processed file with the password using default_storage.save()
            with default_storage.open(processed_file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
              # Remove the original file
            file_obj.close()
            pdf_writer.close()
            os.remove(absolute_file_path)

            # Emailing

            subject = 'Your Protected PDF is Ready'
            message = 'The password protected pdf is attached below:'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]

            msg = MIMEMultipart()
            msg['From'] = email_from
            msg['To'] = ', '.join(recipient_list)
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            # Attach the PDF file
            attachment_path = processed_file_path
            attachment_filename = attachment_path.split('/')[-1]

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(open(attachment_path, 'rb').read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')

            msg.attach(attachment)

            try:
                with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                    if settings.EMAIL_USE_TLS:
                        server.starttls()
                    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                    server.sendmail(email_from, recipient_list, msg.as_string())
                print("Email sent successfully")
            except Exception as e:
                print("Error sending email:", str(e))


            print("MAIL SENT")

            # os.remove(processed_file_path)


             # Add a success message

            messages.success(request, 'File uploaded and password added successfully!')
            return redirect('index')
      
   return render(request,"index.html")