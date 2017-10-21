# flask-form
# 关于flask表单的内容
##用蓝图的时候在蓝图里调用app是，要在user定义之后在引入app。
##刚开始导入数据库表的时候，访问网页可能会有error，捕获到try一下，让他不存在的时候直接建一个数据库表就好，然后第一次查询的时候，由于里面没有数据，会有一个断言error，捕获到pass掉就好

##数据库迁移命令：

```shell
# 创建数据库迁移使用的目录及初始化脚本（执行一次即可）
>>python manage.py db init
# 生成自动化迁移用的脚本程序
>>python manage.py db migrate
# 执行数据库迁移脚本
>>python manage.py db upgrade
# 说明数据库迁移不一定每次都成功，所以每次执行后都需要确认是否有问题，若有问题需要手动解决。
```
