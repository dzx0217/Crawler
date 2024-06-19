# STEPS

## websites

> 每个学校院系下的子网站地址websites，然后找到people list 

## people list

> 教师名录表，每一个教师都是一个超链接，然后可以跳转到对应的教师的个人简介profileurl

## profileurl

> 教师个人简介页面，每个教师有各自的简介页面，通过检索这个页面，然后获取到name，field，location等属性

## pubmed 🆗

> 待做：查找是否有pubmed API，在pubmed中查找对应教师的文献等



```mermaid
graph TD
    A[开始] --> B1[步骤 1: 获取学校院系的子网站地址 websites]
    B1 --> C[步骤 2: 找到教师名录 people list]
    C -->|访问名录页面| C1[抓取教师名录和个人简介链接]
    C1 --> D[步骤 3: 获取教师个人简介 profileurl]
    D -->|访问教师个人简介页面| D1[解析页面获取 name, field, location]
    D1 --> E[步骤 4: 在PubMed中查找教师文献]
    E -->|使用教师信息| E1[构建PubMed查询]
    E1 --> F[结束]
    
    
```



