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
package org.trustedanalytics.sparktk.frame.internal.rdd

import org.apache.spark.sql.Row

/**
 * Ordering for sorting key-value RDDs by key
 * 排序按键排序键值RDD
 * The key is a list of column values. Each column is ordered in ascending or descending order.
 * 关键是列值的列表,每列按升序或降序排列
 * @param ascendingPerColumn Indicates whether to sort each column in list in ascending (true)
 *                           or descending (false) order
 */
class MultiColumnKeyOrdering(ascendingPerColumn: List[Boolean]) extends Ordering[(List[Any], Row)] {
  val multiColumnOrdering = new MultiColumnOrdering(ascendingPerColumn)

  override def compare(a: (List[Any], Row), b: (List[Any], Row)): Int = {
    multiColumnOrdering.compare(a._1, b._1)
  }
}
