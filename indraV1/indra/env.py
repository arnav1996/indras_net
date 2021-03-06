"""
env.py
Our base environment class for hosting agents.
Other specialized environments inherit from this.
"""

from collections import deque
# import sys
import time
import pdb
import getpass
import networkx as nx
import indra.display_methods as disp
import indra.data_methods as data
import indra.node as node
import indra.main_menu as mm
import indra.prop_args2 as pa
import indra.agent_pop as ap
import indra.user as user
import json
import os
import logging

NI = "Not implemented at present."
RPT_EXT = ".csv"

class Quit(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Environment(node.Node):
    """
    A basic environment allowing starting, stopping,
    stepping, inspection and editing of key objects,  etc.
    """

    def __init__(self, name, preact=False,
                 postact=False, model_nm=None, props=None):
        super().__init__(name)

        self.period = 0
        self.preact = preact
        self.postact = postact
        self.disp_census = False
        self.line_graph = None
        self.line_graph_title = "Populations in "
        self.model_nm = model_nm
        if props is None:
            if model_nm is not None:
                self.props = pa.PropArgs.get_props(model_nm)
            else:
                self.props = None
        else:
            self.props = props

        user_nm = getpass.getuser()
        user_type = user.TERMINAL
        if self.props is not None:
            self.props["user_name"] = user_nm
            user_type = self.props["user_type"]
        self.user = user.User(user_nm, user_type)
        # we have to wait until user is set to do...
        if self.props is None:
            self.user.tell("Could not get props; model_nm = " + str(model_nm),
                           type=user.ERROR)
        self.menu = mm.MainMenu("Main Menu", self)

        self.image_bytes = None

        self.__init_unrestorables()

    def __init_unrestorables(self):
        # anything that can't be restored from JSON file init here
        pop_name = ""
        if self.model_nm:
            pop_name += self.model_nm + " "
        pop_name += "Agents"
        self.agents = ap.AgentPop(pop_name)

        self.womb = []
        self.graph = nx.Graph()
        self.graph.add_edge(self, self.agents)
        if self.props is not None:
            self.graph.add_edge(self, self.props)
        self.graph.add_edge(self, self.user)
        self.graph.add_edge(self, self.menu)
        self.graph.add_edge(self, node.universals)

    def add_variety(self, var):
        self.agents.add_variety(var)

    def add_agent(self, agent):
        """
        Add an agent to pop.
        """
        self.agents.append(agent)
        agent.add_env(self)

    def remove_agent(self, agent):
        """
        Remove agent from pop.
        """
        self.agents.remove(agent)

    def join_agents(self, a1, a2):
        """
        Relate two agents.
        """
        self.agents.join_agents(a1, a2)

    def add_child(self, agent):
        """
        Put a child agent in the womb.
        """
        self.womb.append(agent)
        agent.add_env(self)

    def find_agent(self, name):
        """
        Find an agent by name.
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_agents_of_var(self, var):
        """
        Return all agents of type 'var'.
        """
        return self.agents.get_agents_of_var(var)

    def get_randagent_of_var(self, var):
        return self.agents.get_randagent_of_var(var)

    def run(self, periods=-1, random=False):
        """
        This is the main menu loop for all models.

        resume: starts up from a previous period.
        periods: run x periods, for batch mode or timing purposes.
        """

        print("Periods = " + str(self.period))
        if periods > -1:
            count = 0
            self.user.tell("Census:")
            while count < periods:
                self.step(random=random)
                count += 1
            if count > 0:
                self.user.tell("Ran for " + str(count) + " periods.\n")
            file_nm = self.props.get(pa.DATAFILE)
            if file_nm is None:
                file_nm = self.model_nm+RPT_EXT
            self.pop_report(file_nm=file_nm)
            return self
        else:
            self.user.tell("Welcome, " + self.user.name)
            self.user.tell("Running in " + self.name)
            #If run in a terminal, display the menu
            if(self.user.utype in
               [user.TERMINAL, user.IPYTHON, user.IPYTHON_NB, user.WEB]):
                msg = self.menu.display()
                while msg is None:
                    try:
                        msg = self.menu.display()
                        self.user.tell("\nMain Menu; Period: " + str(self.period))
                    except Quit:
                        break
                self.user.tell(msg)

    def add_menu_item(self, submenu, letter, text, func):
        """
        This func exists to screen the menu class from outside objects:
        no need for them to know more than the env
        """
        self.menu.add_menu_item(submenu, letter, text, func)

    def debug(self):
        """
        Invoke the python debugger.
        """
        pdb.set_trace()

    def eval_code(self):
        """
        Evaluate a line of code.
        """
        eval(self.user.ask("Type a line of code to run: "))

    def list_agents(self):
        """
        List all agents in env.
        """
        self.user.tell("Active agents in environment:", text_id=1, reverse=False)
        for agent in self.agents:
            self.user.tell(agent.name
                           + " with a goal of "
                           + agent.goal, text_id=1, reverse=False)

    def add(self):
        """
        Add a new agent to the env.
        """
        if self.props is not None:
            exec("import " + self.props["model"]
                 + " as m")
            constr = self.user.ask("Enter constructor for agent to add: ")
            new_agent = eval("m." + constr)
            self.add_agent(new_agent)
        else:
            self.user.tell("Props missing; can't add agent.", type=user.ERROR)

    def agent_inspect(self, agent_nm=None):
        """
        View (and possibly alter) an agent's data.
        """
        if not agent_nm:
            agent_nm = self.user.ask(
                "Type the name of the agent to inspect: ")
            if not agent_nm:
                return None

        agent = self.find_agent(agent_nm.strip())
        if agent is None:
            self.user.tell("No such agent")
        else:
            self.user.tell(agent.debug_info())
        # self.edit_field(agent)
        # above line out until we get first test working
        return agent

    def pprint(self):
        self.user.tell(NI)

    def env_inspect(self):
        """
        Have a look at (and possibly alter) the environment.
        """
        self.pprint()
        # self.edit_field(self)

    def edit_field(self, entity):
        """
        Edit a field in an entity.
        """
        while True:
            y_n = self.user.ask("Change a field's value in "
                                + entity.name
                                + "? (y/n) "
                                + "(Only str, float, and int supported.)")
            if y_n in ["Y", "y"]:
                field = self.user.ask("Which field? ")
                nval = self.user.ask("Enter new value for "
                                     + field + ": ")
                fld_type = type(entity.__dict__[field])
                if fld_type is int:
                    entity.__dict__[field] = int(nval)
                elif fld_type is float:
                    entity.__dict__[field] = float(nval)
                else:
                    entity.__dict__[field] = nval
            else:
                break

    def n_steps(self, steps=None, random=False):
        """
        Run for n steps.
        """
        if steps is None:
            steps = int(self.user.ask("Enter number of steps: "))
        target = self.period + steps
        self.user.tell("Running for %i steps; press Ctrl-c to halt!" % steps)
        time.sleep(3)
        try:
            while self.period < target:
                step_msg = self.step(random=random)
                if step_msg is not None:
                    self.user.tell(step_msg)
                    break
        except KeyboardInterrupt:
            pass

    def pwrite(self, file_nm=None):
        """
        Write out the properties to a file.
        """
        if file_nm is None:
            file_nm = self.user.ask("Choose file name: ")
        if len(file_nm) > 0 and self.props is not None:
            self.props.write(file_nm)
        else:
            self.user.tell("Props can't be written.",
                          type=user.ERROR)

    def disp_props(self):
        """
        Display current system properties.
        """
        if self.props is not None:
            self.user.tell(self.props.display())
        else:
            self.user.tell("Props missing; cannot be displayed.",
                          type=user.ERROR)

    def disp_log(self):
        """
        Display last 16 lines of log file.
        """
        MAX_LINES = 16
        logfile = None

        if self.props is not None:
            logfile = self.props.get_logfile()
        else:
            self.user.tell("Props missing; cannot identify log file!",
                          type=user.ERROR, text_id=1,
                       reverse=False)
            return

        if logfile is None:
            self.user.tell("No log file to examine!", type=user.ERROR, text_id=1,
                       reverse=False)
            return

        last_n_lines = deque(maxlen=MAX_LINES)  # for now hard-coded

        with open(logfile, 'rt') as log:
            for line in log:
                last_n_lines.append(line)

        self.user.tell("Displaying the last " + str(MAX_LINES)
                       + " lines of logfile " + logfile, text_id=1,
                       reverse=False)
        for line in last_n_lines:
            self.user.tell(line.strip(), text_id=1,
                       reverse=False)

    def step(self, random=False):
        """
        Step period-by-period through agent actions.
        """
        self.census(disp=self.disp_census)
        self.period += 1

# agents might be waiting to be born
        if self.womb is not None:
            for agent in self.womb:
                self.add_agent(agent)
            del self.womb[:]

# there might be state-setting to do before acting
        if self.preact:
            self.preact_loop()

# now have everyone act
        self.act_loop(random)

# there might be state-setting to do after acting
        if self.postact:
            self.postact_loop()

    def act_loop(self, random=False):
        """
        Loop through randomly through agents calling their act() func.
        """
        if random:
            for agent in self.agents.agent_random_iter():
                agent.act()
        else:
            for agent in self.agents:
                agent.act()

    def preact_loop(self):
        """
        Loop through agents calling their preact() func.
        """
        for agent in self.agents:
            agent.preact()

    def postact_loop(self, random=False):
        """
        Loop through agents calling their postact() func.
        """
        if random:
            for agent in self.agents.agent_random_iter():
                agent.postact()
        else:
            for agent in self.agents:
                agent.postact()

    def graph_agents(self):
        """
        Draw a graph of the agent relationships.
        """
        self.agents.draw()

    def graph_env(self):
        """
        Draw a graph of the env's relationships.
        """
        self.draw()

    def graph_unv(self):
        """
        Draw a graph of the universal relationships.
        """
        node.universals.draw()

    def graph_class_tree(self):
        node.Node.class_draw()

    def keep_running(self):
        """
        Placeholder
        """
        return True

    def view_pop(self):
        """
        Graph our population levels.
        """
        if not disp.plt_present:
            self.user.tell("No graphing package installed", type=user.ERROR)
            return
        if self.period < 4:
            self.user.tell("Too little data to display", type=user.ERROR)
            return

        (period, data) = self.line_data()
        self.line_graph = disp.LineGraph(self.line_graph_title + self.name,
                                         data, period)
        self.line_graph.show()

    def line_data(self):
        return (self.period, self.agents.get_pop_hist())

    def pop_report(self, file_nm=None):
        if file_nm is None:
            file_nm = self.user.ask("Choose file name: ")
        data.pop_report(file_nm, self.agents.get_pop_hist())

    def plot(self):
        """
        Draw a line graph
        """
        (period, data) = self.line_data()
        self.line_graph = disp.LineGraph(self.line_graph_title + self.name,
                                         data, period, is_headless=self.headless())
        self.image_bytes = self.line_graph.show()
        return self.image_bytes

    def headless(self):
        if not disp.plt_present:
            self.user.tell("No graphing package installed", type=user.ERROR)
            return
        headless = False
        if self.user.utype == user.WEB:
            headless = True
        return headless

    def quit(self):
        """
        Leave this run.
        """
        self.user.tell("Exiting main loop.")
        raise Quit("User exit")

    def contains(self, agent_type):
        """
        Do we have this sort of thing in our env?
        """
        return self.agents.contains(agent_type)

    def census(self, disp=True, exclude_var=None):
        """
        Take a census of what is in the env.
        """
        results = self.agents.census(exclude_var=exclude_var)
        if disp:
            self.user.tell("Populations in period "
                           + str(self.period) + ":\n" + results)

    def test_hook(self, **kwargs):
        return None

    def varieties_iter(self):
        return self.agents.varieties_iter()

    def variety_iter(self, var):
        return self.agents.variety_iter(var)

    def set_var_color(self, var, color):
        self.agents.set_var_color(var, color)

    def get_pop(self, var):
        """
        Return the population of variety 'var'
        """
        return self.agents.get_pop(var)

    def get_total_pop(self):
        """
        Return the total number of agents.
        """
        return self.agents.get_total_pop()

    def get_my_pop(self, agent):
        """
        Return the population of agent's type
        """
        return self.agents.get_my_pop(agent)

    def change_agent_type(self, agent, old_type, new_type):
        self.agents.change_agent_type(agent, old_type, new_type)

    def record_results(self, file_nm):
        self.agents.record_results(file_nm)

    def change_pop_data(self, var, change):
        self.agents.change_pop_data(var, change)

    def get_pop_data(self, var):
        return self.agents.get_pop_data(var)

    def append_pop_hist(self, var, pop):
        self.agents.append_pop_hist(var, pop)

    def get_var_pop_hist(self, var):
        return self.agents.get_var_pop_hist(var)

    def to_json(self):
        #Serialize the env
        safe_fields = super().to_json()
        safe_fields["period"] = self.period
        safe_fields["model_nm"] = self.model_nm
        safe_fields["preact"] = self.preact
        safe_fields["postact"] = self.postact

        #Serialize objects
        safe_fields["props"] = self.props.to_json()
        safe_fields["user"] = self.user.to_json()

        #Serialize agents
        safe_fields["agents"] = self.serialize_list(self.agents)
        safe_fields["pop_hist"] = self.agents.get_pop_hist()
        safe_fields["womb"] = self.serialize_list(self.womb)

        return safe_fields

    def serialize_list(self, serializable_list):
        return [agent.to_json() for agent in serializable_list]

    def save_session(self, session_id=None):
        """
        Save the current session to a json file
        """
        try:
            base_dir = self.props["base_dir"]
        except:
            base_dir = ""

        if session_id is None:
            session_id = self.user.ask("Enter session id: ")
        session_id = str(session_id)

        json_output = str(json.dumps(self.to_json()))
        path = os.path.join(base_dir, "json/" + self.model_nm + session_id + ".json")
        with open(path, "w+") as f:
            f.write(json_output)

        #self.print_env()
        #self.user.tell("Session saved")

    def restore_session(self, session_id=None):
        """
        Restore a previous session from a json file
        """
        logging.info("-------------------------Start Restoration of states-------------------------------")

        try:
            base_dir = self.props["base_dir"]
        except:
            base_dir = ""

        if session_id is None:
            session_id = str(self.user.ask("Enter session id: "))
        session_id = str(session_id)
        path = os.path.join(base_dir, "json/" + self.model_nm + session_id + ".json")
        with open(path, "r") as f:
            json_input = f.readline()
        json_input = json.loads(json_input)
        self.from_json(json_input)

        self.restore_agents(json_input)
        self.restore_womb(json_input)
        self.agents.restore_hist_from(json_input["pop_hist"])

        #self.print_env()
        #self.user.tell("Session restored")

    def from_json(self, json_input):
        self.__init_unrestorables()

        self.name = json_input["name"]
        self.preact = json_input["preact"]
        self.postact = json_input["postact"]
        self.model_nm = json_input["model_nm"]
        self.props = pa.PropArgs(self.model_nm, prop_dict=json_input["props"])
        self.period = json_input["period"]
        self.user.from_json(json_input["user"])

    def restore_agents(self, json_input):
        """
        Restore the states of all agents
        """
        for agent in json_input["agents"]:
            self.restore_agent(agent)

    def restore_womb(self, json_input):
        for agent in json_input["womb"]:
            self.restore_womb_agent(agent)

    def restore_womb_agent(self, agent_json):
        logging.info("restore_womb_agent not implemented")

    def restore_agent(self, agent_json):
        logging.info("restore_agent not implemented")

    def print_env(self):
        logging.info("print_env not implemented")
