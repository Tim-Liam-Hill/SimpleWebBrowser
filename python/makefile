init: requirements.txt
	pip install -r requirements.txt

test: 
	python3 -m unittest 
# if we want to only test certain modules we can possible do 
#python3 -m unittest <module_name>.py or package name or whatever
#only really needed if certain tests take too long to run. 


clean:
	find -type d -name __pycache__ -a -prune -exec rm -rf {} \;