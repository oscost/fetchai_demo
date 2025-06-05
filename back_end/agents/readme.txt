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
        Will query ASI1 or another LLM in order to find answers to whatever patterns we have
        identified. Additionally will give explinations on why such changes will alter the
        effect half of the discovered pattern. It can also give notes on things you are
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

    Messenger:
        On a new daily log will start the process of extraction. This will eventually lead
        to our pattern matcher. If we pick up a new trend this will triger our planner.

        If we notice concerning behavior and if the user allows for contacts to be messaged
        when concerning behavior is flagged it will notify contacts with a brief summary.

        All our agents communicate through the messenger. This is to reduce abstract away
        communication semantics in each specific agent and give each agent messages in an
        expected format.
    
