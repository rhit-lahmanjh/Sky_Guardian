import torch



if torch.cuda.is_available():
    device = "cuda:0"
    print("Converted for GPU")
else:
    device = "cpu"
    print("Converted for CPU")
device = "cpu"

model = torch.load("yolov8s.pt")


torch.onnx.export(model,                                # model being run
                  torch.randn(1, 28, 28).to(device),    # model input (or a tuple for multiple inputs)
                  "yolov8s.onnx",           # where to save the model (can be a file or file-like object)
                  input_names = ['input'],              # the model's input names
                  output_names = ['output'])            # the model's output names


