#----未知状态----
UNKNOW_STATE = "UNKNOW"

#----算子的状态----
#flow manager解析完工作流，遍历各算子并提交slurm前设置该算子状态为queued-->flow_processor.process_actors()
ACTOR_STATE_QUEUED = "QUEUED"
#slurm申请到节点，但还没开始消费时，状态为READY-->actor_wrapper.if __name__ == '__main__'
ACTOR_STATE_READY = "READY"
#开始消费后状态为RUNNING-->actor_wrapper.process_source_actor()和actor_wrapper.loop_input_port()
ACTOR_STATE_RUNNING = "RUNNING"
#(定时任务)根据slurm的scontrol命令来判断timer.update_actor_state()
ACTOR_STATE_SUCCESS = "SUCCESS"
ACTOR_STATE_FAILED = "FAILED"
ACTOR_STATE_CANCELLED = "CANCELLED"
ACTOR_STATE_STOPPABLE = "STOPPABLE"

# redis key
# 算子间的关系
REDIS_KEY_FOR_ACTOR_RELATION = 'flow_manager_for_actor_relation'
# 算子的状态
REDIS_KEY_FOR_ACTOR_STATE = 'flow_manager_for_actor_state'
# 算子的整体状态
REDIS_KEY_FOR_ACTOR_FINAL_STATE = 'flow_manager_for_actor_final_state'
# # jobId和算子间的关系
# REDIS_KEY_FOR_JOB_MAPPING = 'flow_manager_for_job_mapping'