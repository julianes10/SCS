# SCS
Software Components Store. Miscellaneous libs, scripts ready to be used in other specific project repositories

Backwards compatible evoluton is key in every reusable component.

Use git submodules for integrating the component in other repositories.

## How to deploy several pi instances of the same service 
In the project you use SCS, just link same service with different names
Configuration file name in project pi/etc shall have the same basename of this link plus .conf
Deployment script will custom service files so that it has different life cycle, configuration etc...

It also allow several project to be installed in the same target and using different instances of the same service, e.g 2 telegram channels, one for failsafe rescue mode (e.g sru) and other with operative main application.

## References
* https://blog.github.com/2016-02-01-working-with-submodules/ 
* https://www.atlassian.com/blog/git/git-submodules-workflows-tips


