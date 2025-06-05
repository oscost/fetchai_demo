Plan for architecure

Agents:
    Extractor:
        Creates a list brief list of what the user did in a daily entry. 
        Ex: [shower,breakfast, run, study, gym, break, phone, sleep].
        Will omit the more unimportant details, but should be able to paint a good picture
        of what happened that day.
        
        Additionally will create a short sentiment analysis of the day. Ideally will give it
        on different slices of the day.
        Ex: [sad, productive, lazy, content]

    Pattern Finder:
        Finds a confidence level between trends to identify what daily habits/activities are
        changing mood and energy levels in meaningful ways
        
        Returns the activities and their resulting effect as well as a confidence level
        that is deterministically calculated. This confidence level is a running-count and
        is not constantly recalculated, but rather it progressively changes.This allows us
        to account for curation more easily.
    
    Planner:
        Will query ASI1 in order to find answers to whatever patterns we have
        identified. Additionally will give explinations on why such changes will alter the
        effect of the discovered pattern. It can also give notes on things you are
        doing well already.
    
    Curator:
        Overtime there will be feedback from the user. The curator will take this feedback
        along with our confidence levels and try to formulate alternate suggestions or 
        decide it unnecesary to try to resolve a specific problem. We can also use
        positive feedback to enchance our confidence levels. 

        Ideally we want the user input to be a big part of our decision making. If they say
        that something is infeasable or are confident it is not working we will take the
        suggestion strongly.

        Important note: The curator is not giving the new plans, but formulating feedback
        on what is and is not important to change. It is then piped into the planner for new
        suggestions. We want our curated reccomendations to be reasonably stable
        so we will keep them locked unless we have big changes in our confidence level.

    

Plan for what to do next:
    Pattern_finder will pipe into our curator. ONLY if we deem it neccesary, we are to
    tell Pattern_finder to send to Planner.
    Create the curator to guage what needs to be altered. Also allow for us to properly
    modify confidence levels in patterns with our curator.

    Have our front end trigger the uAgent pipeline.
    (namely extractor. NOTE basically what our test script does)

    Have our front end properly communicate with our pipeline. This way we are displaying
    what is intended.