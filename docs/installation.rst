.. highlight:: shell

============
Installation
============


mkdir -p ~/.pip

~/.pip/pip.conf

add

[global]
trusted-host=pypi.devops.videt.cn
extra-index-url=http://pypi.devops.videt.cn/videt/repo



~/.pydistutils.cfg

add


[easy_install]
 
find_links = http://pypi.devops.videt.cn/videt/repo


pip install videt-dar-sg-customs-pcg-packinglist-grpc
