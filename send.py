import pymysql
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 数据库连接配置
db_config = {
    'host': 'localhost',       # 数据库服务器地址
    'user': 'admin',   # 数据库用户名
    'password': '123456', # 数据库密码
    'db': 'professors',       # 数据库名
    'charset': 'utf8mb4',      # 字符集
    'cursorclass': pymysql.cursors.DictCursor  # 使用字典形式的游标
}

# 邮件发送配置
mail_config = {
    'smtp_server': 'smtp.example.com',  # SMTP服务器地址
    'port': 587,                         # SMTP端口
    'username': 'your_email@example.com', # 发件人邮箱
    'password': 'your_email_password',   # 发件人邮箱密码
    'from_name': 'Your Name',            # 发件人名称
    'from_addr': 'your_email@example.com' # 发件人邮箱地址
}

# 连接数据库
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # 执行SQL查询
        sql = "SELECT email FROM people"
        cursor.execute(sql)
        results = cursor.fetchall()

        # 遍历查询结果
        for email in results:
            email_address = email['email']

            # 创建邮件内容
            msg = MIMEText('Hello, this is an automated email.', 'plain', 'utf-8')
            msg['From'] = Header(mail_config['from_name'], 'utf-8')
            msg['To'] = email_address
            msg['Subject'] = Header('Automated Email Subject', 'utf-8')

            # 发送邮件
            server = smtplib.SMTP(mail_config['smtp_server'], mail_config['port'])
            server.starttls()
            server.login(mail_config['username'], mail_config['password'])
            server.sendmail(mail_config['from_addr'], [email_address], msg.as_string())
            server.quit()

            print(f"Email sent to {email_address}")

finally:
    connection.close()

print("Email sending process completed.")