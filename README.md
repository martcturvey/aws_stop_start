AWS resource stop/start with boto

Usage:  
python *service*_[start|stop].py *name*

For EC2 and ASG, looks for a tag Name:*name* against the resource  
For RDS, looks for RDS instance called *name*
