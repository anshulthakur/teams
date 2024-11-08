# Test Execution And Maintenance System (TEAMS)

TEAMS has been developed in response to the requirement of gathering telemetry data on test cases for a small group/team.
Being a lazy person myself when it comes to test documentation, but also being a developer at heart, I want to remove as 
much friction between creating/updating test cases and getting a bird's eye view of how we're doing.

In particular, TEAMS hopes to solve the following problems:

1. **Maintaining multiple copies of Test Case Docs**: We all revise, but often forget to merge everything back together. 
So, one, web based platform to maintain tests, so that multiple copies do not create confusion. Work on a single copy.
2. **Creating the initial Test Case Doc skeleton**: Getting started is the hardest part. So, instead of having to worry 
about formatting your text, you can focus on putting the right content in the right place. You can export a docx which 
closely resembles your test case document (and can be customized as per group requirements).
3. **Statistics on test executions**: Test Cases are created once but executed multiple times. We want to keep track 
of how many times it is run, and how many times it has succeeded/failed etc. When multiple tests run, some may fail. 
I want to help quantify this, and help figure out where the pain points are. I believe, data wrangling can help do that.
Test Executions (grouped under Test Runs) can be manually maintained, or an automation framework may push the results 
automatically using the REST API provided. Right now, I've integrated this API with my Automation framework as well.


## Under the hood (for developers/contributors)
- The backend is written in Django (a python based web development framework).
- The frontend is written as a mix of `htmx` and `react`. `htmx` is for tiny interactions with the backend, for example,
deleting a test case/suite/run. `React` is for larger use cases, such as test case form rendering, DOM manipulation.
- Automation API uses JWT authentication to avoid CSRF problem. For the WebInterface, session-cookie based authentication 
(and CSRF validation) are used.
- For single-user-signon, we are using OpenLDAP currently. In order to run properly, the development libraries must be present. 
On a Debian based system, the same may be installed as

```
apt-get install build-essential python3-dev \
    libldap2-dev libsasl2-dev slapd ldap-utils tox \
    lcov valgrind
```