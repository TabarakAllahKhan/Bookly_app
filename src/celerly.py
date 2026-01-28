from celery import Celery
from src.config import Config
from redmail import gmail

gmail.username=Config.GMAIL
gmail.password=Config.GMAIL_PASSWORD
celery_app=Celery()

celery_app.config_from_object('src.config')

@celery_app.task
def send_email(receivers=None, subject=None, text=None, html=None, **kwargs):
     try:
          # redmail.gmail.send is synchronous and returns an EmailMessage object.
          message = gmail.send(
               subject=subject,
               receivers=receivers,
               text=text,
               html=html,
               **kwargs,
          )
          return {"status": "sent", "result": str(message)}
     except Exception as e:
          return {"status": "error", "error": str(e)}
 