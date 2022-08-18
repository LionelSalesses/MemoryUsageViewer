from subprocess import Popen, PIPE


class CmdExecError(Exception):
    def __init__(self, cmd, args, cmdExitCode, cmdStdOut, cmdStdErr):
        super().__init__()
        self.cmd = cmd
        self.args = args
        self.cmdExitCode = cmdExitCode
        self.cmdStdOut = cmdStdOut
        self.cmdStdErr = cmdStdErr
    
    def getMessage(self):
        msg = "<blockquote>"
        msg += "<u>Command:</u> '<i>" + self.cmd + " " + " ".join(self.args) + "</i>'"
        msg += "<br>"
        msg += "<u>Exit code:</u> <i>" + str(self.cmdExitCode) + "</i>"
        msg += "<br>"
        if len(self.cmdStdOut) > 0:
            msg += "<u>Output:</u> <i>" + self.cmdStdOut + "</i>"
            msg += "<br>"
        if len(self.cmdStdErr) > 0:
            msg += "<u>Error:</u> <i>" + self.cmdStdErr + "</i>"
            msg += "<br>"
        msg += "</blockquote>"
        return msg


def execCommand(cmd, args):
    process = Popen([cmd] + args, stdout=PIPE, stderr=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    if exit_code != 0:
        raise CmdExecError(
            cmd,
            args,
            exit_code,
            output.decode("utf-8").rstrip('\r\n'),
            err.decode("utf-8").rstrip('\r\n'), 
        )
    return output


class SmemProxy:
    def __init__(self):
        pass
    
    COLUMNS = ['Command line', 'PID', 'RSS', 'PSS', 'USS']
    
    @staticmethod
    def checkSupport():
        try:
            result = execCommand("smem", ["--help"])
        except (FileNotFoundError, CmdExecError):
            return False
        return True
    
    def parseLine(self, line):
        ll = line.split(' ')
        ll = [int(l) for l in ll if len(l) > 0]  # Skip ''
        return ll
    
    def parseSmemOutput(self, rawOutput):
        lines = rawOutput.split('\n')
        totalLine = lines[-2]  # Extract line displaying totals
        lines = lines[:-3]  # Skip lines used to display totals
        return [self.parseLine(l) for l in lines]
    
    def getSmemData(self):
        columns = ['pid', 'rss', 'pss', 'uss']
        result = execCommand("smem", ["-t", "-n", "-H", "-c", ' '.join(columns)])
        result = result.decode("utf-8")
        smemData = self.parseSmemOutput(result)
        # Multiply RSS, PSS, USS by 1024 because they are given in KB by smem
        for i in range(len(smemData)):
            smemData[i][1] *= 1024
            smemData[i][2] *= 1024
            smemData[i][3] *= 1024
        return smemData
    
    @staticmethod
    def getCmdLineFromPID(pid):
        assert isinstance(pid, int)
        result = execCommand("ps", ["-w", "-w", "-p", str(pid), "-o", "cmd", "h"])
        cmdLine = result.decode("utf-8").rstrip('\r\n')
        return cmdLine
    
    def getCmdLineData(self, pidList):
        pidToCmd = {}
        for pid in pidList:
            try:
                cmdLine = self.getCmdLineFromPID(pid)
            except CmdExecError:
                # Process cmd line is not accessible. May happens when processes finished, for example
                # smem process itself.
                print("Cannot read command line of process with pid=", pid)
                continue
            pidToCmd[pid] = cmdLine
        return pidToCmd
        
    def formatData(self, smemData, pidToCmd):
        formattedData = []
        for row in smemData:
            pid = row[0]
            if pid in pidToCmd:
                cmdLine = pidToCmd[pid]
                row_ = row.copy()
                row_.insert(0, cmdLine)
                formattedData.append(row_)
            else:
                # Command line is not available, process skipped
                pass
        return formattedData, self.COLUMNS
    
    def getData(self):
        data = self.getSmemData()
        pidToCmd = self.getCmdLineData([d[0] for d in data])
        return self.formatData(data, pidToCmd)

