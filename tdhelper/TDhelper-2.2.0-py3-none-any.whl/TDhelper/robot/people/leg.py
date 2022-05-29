from TDhelper.robot.people import action, actionMode
from TDhelper.robot.struct.base import joint
from TDhelper.robot.struct.toe import TOE
from TDhelper.robot.struct.ankle import ANKLE
from TDhelper.robot.struct.knee import KNEE
from TDhelper.robot.struct.hip import HIP
from TDhelper.robot.control.D_33890 import device_D_33890


class LEGS(action):
    def __init__(self):
        super(LEGS, self).__init__()
        self.leftTOE = []
        self.rightTOE = []
        self.leftTOE = self._generateToes(label="左")
        self.rightTOE = self._generateToes(label="右")
        self.leftANKLE = self._generateAnkles(label="左")
        self.rightANKLE = self._generateAnkles(label="右")
        self.leftKNEE = self._generateKnees(label="左")
        self.rightKNEE = self._generateKnees(label="右")
        self.leftHIP = self._generateHips(label="左")
        self.rightHIP = self._generateHips(label="右")

    def _generateHips(self, label: str = ''):
        '''
            生成胯关节
        '''
        m_joints = []
        power = {
            'updown': device_D_33890("%s胯关节上下舵机" % label, (0, 180), 90),
            'leftright': device_D_33890("%s胯关节左右舵机" % label, (0, 180), 90)
        }
        m_joints.append(joint('%s胯' % label, powerSystem=power))
        return HIP(m_joints)

    def _generateKnees(self, label: str = ""):
        '''
            生成膝盖关节
        '''
        m_joints = []
        power = {
            'updown': device_D_33890("%s膝盖关节上下舵机" % label, (0, 140), 0)
        }
        m_joints.append(joint('%s膝盖' % label, powerSystem=power))
        return KNEE(m_joints)

    def _generateAnkles(self, label: str = ""):
        '''
            生成脚踝
        '''
        m_joints = []
        power = {
            'updown': device_D_33890("%s踝关节上下舵机" % label, (0, 90), 0),
            'leftright': device_D_33890("%s踝关节左右舵机" % label, (0, 90), 45)
        }
        m_joints.append(joint('%s脚踝' % label, powerSystem=power))
        return ANKLE(m_joints)

    def _generateToes(self, label: str = ''):
        '''
            生成脚趾
        '''
        ret = [None, None, None, None, None]
        m_joints = []
        # 大脚趾
        power = {
            'updown': device_D_33890("%s脚大拇趾第一关节" % label, (0,90),0)
        }
        m_joints.append(joint('%s脚大拇指第一关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚大拇趾第二关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚大拇指第二关节' % label, powerSystem=power))
        ret[0] = TOE(m_joints)
        # 二号脚趾
        m_joints.clear()
        power = {
            'updown': device_D_33890("%s脚第二脚趾指第一关节" % label,(0,90),0)
        }
        m_joints.append(joint('%s脚第二脚趾指第一关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第二脚趾指第二关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第二脚趾指第二关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第二脚趾指第三关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第二脚趾指第三关节' % label, powerSystem=power))
        ret[1] = TOE(m_joints)
        # 三号脚趾
        m_joints.clear()
        power = {
            'updown': device_D_33890("%s脚第三脚趾指第一关节" % label, (0,90),0)
        }
        m_joints.append(joint('%s脚第三脚趾指第一关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第三脚趾指第二关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第三脚趾指第二关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第三脚趾指第三关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第三脚趾指第三关节' % label, powerSystem=power))
        ret[2] = TOE(m_joints)
        # 四号脚趾
        m_joints.clear()
        power = {
            'updown': device_D_33890("%s脚第四脚趾指第一关节" % label, (0,90),0)
        }
        m_joints.append(joint('%s脚第四脚趾指第一关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第四脚趾指第二关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第四脚趾指第二关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第四脚趾指第三关节" % label,  (-90,0),0)
        }
        m_joints.append(joint('%s脚第四脚趾指第三关节' % label, powerSystem=power))
        ret[3] = TOE(m_joints)
        # 五号脚趾
        m_joints.clear()
        power = {
            'updown': device_D_33890("%s脚第五脚趾指第一关节" % label, (0,90),0)
        }
        m_joints.append(joint('%s脚第五脚趾指第一关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第五脚趾指第三关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第五脚趾指第二关节' % label, powerSystem=power))
        power = {
            'updown': device_D_33890("%s脚第五脚趾指第三关节" % label, (-90,0),0)
        }
        m_joints.append(joint('%s脚第五脚趾指第三关节' % label, powerSystem=power))
        ret[4] = TOE(m_joints)
        return ret
