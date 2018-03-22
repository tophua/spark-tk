/**
 *  Copyright (c) 2016 Intel Corporation 
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
package org.trustedanalytics.sparktk.frame.internal.ops.join

import org.trustedanalytics.sparktk.frame.{ SchemaHelper, DataTypes, Frame }
import org.trustedanalytics.sparktk.frame.internal.rdd.FrameRdd
import org.trustedanalytics.sparktk.frame.internal.{ FrameState, FrameSummarization, BaseFrame }

trait JoinLeftSummarization extends BaseFrame {

  /**
   * Join operation on one or two frames, creating a new frame.
   * 加入一个或两个frames的操作,创建一个新的frames
   * @param right Another frame to join with. 另一frames加入
   * @param leftOn Names of the columns in the left frame used to match up the two frames.
    *               用于匹配两个框架的左侧框架中的列的名称
   * @param rightOn Names of the columns in the right frame used to match up the two frames. Default is the same as the left frame.
    *                用于匹配两个框架的右侧框架中的列的名称,默认值与左边框相同。
   * @param useBroadcastRight If right table is small enough to fit in the memory of a single machine, you can set useBroadcastRight to True to perform broadcast join.
    *                          如果右表足够小以适应单个机器的内存,则可以将useBroadcastRight设置为True来执行广播连接
   * Default is False.
   */
  def joinLeft(right: Frame,
               leftOn: List[String],
               rightOn: Option[List[String]] = None,
               useBroadcastRight: Boolean = false): Frame = {
    execute(JoinLeft(right, leftOn, rightOn, useBroadcastRight))
  }
}

case class JoinLeft(right: Frame,
                    leftOn: List[String],
                    rightOn: Option[List[String]],
                    useBroadcastRight: Boolean) extends FrameSummarization[Frame] {

  require(right != null, "right frame is required")
  require(leftOn != null || leftOn.nonEmpty, "left join column is required")
  require(rightOn != null, "right join column is required")

  override def work(state: FrameState): Frame = {

    val leftFrame: FrameRdd = state
    val rightFrame: FrameRdd = new FrameRdd(right.schema, right.rdd)

    //first validate join columns are valid
    //首先验证连接列是有效的
    val leftColumns = leftOn
    val rightColumns = rightOn.getOrElse(leftOn)

    //First validates join columns are valid and checks left join column is compatible with right join columns
    //首先验证连接列是否有效,并检查左连接列是否与右连接列兼容
    SchemaHelper.checkValidColumnsExistAndCompatible(leftFrame, rightFrame, leftColumns, rightColumns)

    val joinedFrame = JoinRddFunctions.leftJoin(
      RddJoinParam(leftFrame, leftColumns),
      RddJoinParam(rightFrame, rightColumns),
      useBroadcastRight
    )
    new Frame(joinedFrame, joinedFrame.schema)
  }
}