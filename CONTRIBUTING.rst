.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/aglavic/ba_tools/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Version of BornAgain and if it was compiled or binary distribution
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

If you extend the software for your own use, please consider adding these improvements
to the ba_tools repository so others can profit from it.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/aglavic/ba_tools/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `ba_tools` for local development.

1. Fork the `ba_tools` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/ba_tools.git

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, auto format the code and check that your changes confirms to PEP 8::

    $ black -l 120 ba_tools
    $ isort -l 120 --lbt 1 ba_tools
    $ flake8 --max-line-length=120 --ignore=F401,W503 --count --show-source --statistics ba_tools

   To get flake8, black and isort, just pip install them into your environment.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

I have not defined any clear guidelines for contributions, yet. I will review each pull request and
possibly propose changes to keep it coherent with the API and quality. But the main focus
of the project is to add functionality and aid the modling workflow, thus features
are more important than coding practices.
