# Boa
A simple Python hypertext processor that works as an "extension" for Flask/Django.

Why did I choose this name? Well, in the Python universe we have a few references to... uh... snakes, such as Python itself, Anaconda etc. And guess what, [Boas](https://en.wikipedia.org/wiki/Boidae) are a snake family.

## (Dis?)advantages
- It sucks!
- ~~It's super slow, forcing you to use PyPy!~~ Has been optimized since. No need for PyPy anymore.
- It sucks!
- Single `.py` file to handle hypertext processing!
- Around ~~300~~ 200 lines of super high quality and high fidelity™ code!
- Templating support (like Jinja's {% block ... %} and {% extends ... %})!
- Custom components (you can make your own HTML tags pretty much)!
- Did I mention it sucks?
- Compatible with Flask, Django and whatever other Python framework, I hate myself and I want to die.

## How does it work?
Well, it's fairly simple. Read the code and you'll understand ;)
Also, check [examples](../examples)

## Warnings
This is most likely vulnerable to XSS and SQL Injection. Do not use this in production for the love of God.
