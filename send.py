import mysql.connector
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库服务器地址
    'user': 'admin',       # 数据库用户名
    'password': '123456',   # 数据库密码
    'database': 'outsourcing'    # 数据库名
}

# 邮件发送配置
sender_qq = 'm20genomics@qq.com'
pwd = 'lkiaqiyiafqtdedg'
host_server = 'smtp.qq.com'
mail_title = 'Python自动发送的邮件'
mail_content = "您好，我们是M20Genomics"

# 连接数据库
db = mysql.connector.connect(**db_config)
cursor = db.cursor()

try:
    # 执行SQL查询
    cursor.execute("SELECT email FROM outsourcing.people")
    # 获取所有邮件地址
    emails = cursor.fetchall()

    # 邮件发送逻辑
    for email in emails:
        print(email[0])
        # receiver = email[0]  # 假设email字段是第一个字段
        #
        # # 初始化邮件
        # msg = MIMEMultipart()
        # msg["Subject"] = Header(mail_title, 'utf-8')
        # msg["From"] = sender_qq
        # msg['To'] = Header(receiver, 'utf-8')  # 确保邮件地址是utf-8编码
        # msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
        #
        # # 发送邮件
        # smtp = SMTP_SSL(host_server)
        # smtp.login(sender_qq, pwd)
        # smtp.sendmail(sender_qq, receiver, msg.as_string())
        # smtp.quit()
        #
        # print(f"邮件已发送至: {receiver}")
        if email[0] == "dzx0217@qq.com":
            receiver = email[0]  # 假设email字段是第一个字段

            # 初始化邮件
            msg = MIMEMultipart()
            msg["Subject"] = Header(mail_title, 'utf-8')
            msg["From"] = sender_qq
            msg['To'] = Header(receiver, 'utf-8')  # 确保邮件地址是utf-8编码
            msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))

            # 发送邮件
            smtp = SMTP_SSL(host_server)
            smtp.login(sender_qq, pwd)
            smtp.sendmail(sender_qq, receiver, msg.as_string())
            smtp.quit()

            print(f"邮件已发送至: {receiver}")

except mysql.connector.Error as err:
    print(f"数据库错误: {err}")
finally:
    # 关闭数据库连接
    if db.is_connected():
        cursor.close()
        db.close()

print("邮件发送完毕。")