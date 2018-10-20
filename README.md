# WeChatTicket

1. mysql root密码pass
2. 数据库连接配置请修改configs.json,而不用修改settings.py
3. 代理：
sudo uwsgi --plugins=python3 -x socket.xml;
sudo service nginx start;
sudo service nginx reload;
4. log: /var/log/nginx/error.log /var/log/nginx/access.log
[![Build Status](https://travis-ci.com/XuYiFanHHH/WeChatTicket.svg?token=GvnMrYy1tquZ6syvYmtc&branch=master)](https://travis-ci.com/XuYiFanHHH/WeChatTicket)
Ticket management system based on WeChat public platform.
