import xlsxwriter



class ExcelWriter():
  # Create a workbook and add a worksheet.


  workbook = None
  worksheet = None

  @staticmethod
  def define_workbook_worksheet(workbook_name):
     ExcelWriter.workbook = xlsxwriter.Workbook(workbook_name)
     ExcelWriter.worksheet = ExcelWriter.workbook.add_worksheet()


  @staticmethod
  def write_schedule_excel(schedule, time, nb_schedule) :
    row = 0
    col = nb_schedule
    ExcelWriter.worksheet.write(row, col, time)
    row+=1
    # Iterate over the data and write it out row by row.
    for optim in schedule.optimizations:
        if str(optim) != '' :
          if hasattr(optim, 'split_factor'):
            row = max(5, row)
          if optim.__class__.__name__ == "ReorderOptimization":
            row = max(11, row)
          if optim.__class__.__name__ == "FuseOptimization" :
             row = max(16, row)
          if optim.__class__.__name__ == "ParallelOptimization" :
             row = max(20, row)
          if optim.__class__.__name__ == "VectorizeOptimization" :
             row = max(25, row)
          if optim.__class__.__name__ == "UnrollOptimization" :
             row = max(30, row)
          if optim.__class__.__name__ == "ComputeAtOptimization" :
             row = max(35, row)
          ExcelWriter.worksheet.write(row, col, str(optim))
          row += 1


    # Write a total using a formula.
    #ExcelWriter.workbook.close()

  @staticmethod
  def close_workbook():
      ExcelWriter.workbook.close()

