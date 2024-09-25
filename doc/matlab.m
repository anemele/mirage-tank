% ref:https://www.mathworks.com/matlabcentral/answers/490540-how-to-generate-an-argb-mirage-tank
Image1="f.jpg";
Image2="b.jpg";
Image1=importdata(Image1);
Image2=importdata(Image2);
%仅当原图是有Alpha通道的PNG时才需要这两行
% Image1=cat(3,Image1.alpha,Image1.cdata);
% Image2=cat(3,Image2.alpha,Image2.cdata);
%仅当原图是有Alpha通道的PNG时才需要这两行
[Alpha,Color]=MirageTankV2(Image1,Image2);
imwrite(Color,"幻影坦克.png","Alpha",Alpha);



function varargout = MirageTankV2(Image1,Image2,varargin)
%输入两张图，制作幻影坦克！
%Image1和Image2三个维度视为列、行、G/AG/RGB/ARGB三个维度，uint8类型。
%默认情况下，白色背景显示Image1，黑色背景显示Image2。
%可选设置Background1和Background2，必须为uint8标量，表示背景的灰度。
%% 可选参数
Background1=255;
Background2=0;
for a=1:2:length(varargin)
    switch varargin{a}
        case "Background1"
            Background1=varargin{a+1};
        case "Background2"
            Background2=varargin{a+1};
    end
end
%% 尺寸统一化
Background1=double(Background1);
Background2=double(Background2);
[Alpha1,Image1]=ChannelSplit(double(Image1));
[Alpha2,Image2]=ChannelSplit(double(Image2));
[Image1,Image2]=ArrayAdapt(Image1,Image2,"SizeOneCopy",true);
[Alpha1,Alpha2]=ArrayAdapt(Alpha1,Alpha2);
BackgroundDelta=Background1-Background2;
Color=Alpha1.*(Background1-Image1)-Alpha2.*(Background2-Image2);
if BackgroundDelta==0
    warning("提供了两个相同的背景，将输出不透明图像");
    Alpha=[];
else
    Alpha=Color./BackgroundDelta;
end
Color=(Alpha1.*Background2.*(Background1-Image1)+Background1.*Alpha2.*(Image2-Background2))./Color;
Color=uint8(Color*255/max(Color,[],"all"));
Alpha=mean(Alpha,3);
Alpha=uint8(Alpha*255/max(Alpha,[],"all"));
if nargout>1
    varargout={Alpha,Color};
else
    varargout=cat(3,Alpha,Color);
end
end
function [Alpha,Color]=ChannelSplit(Image)
Alpha=Image(:,:,1);
if bitand(size(Image,3),1)
    Alpha(:)=255;
    Color=Image;
else
    Color=Image(:,:,2:end);
end
end
function varargout = ArrayAdapt(varargin)
%将输入的所有数组每个维度扩展到所有数组在该维度的最大值
%% 可选参数
%NullValue，标量，扩展时所用的填充值，默认0
%SizeOneCopy，逻辑标量，如果一个数组某一维度尺寸为1，是否以复制而非NullValue填充的方式扩展该维度，默认false。
%% 默认参数
NullValue=0;
SizeOneCopy=false;
a=1;
while a<=length(varargin)
    Argument=varargin{a};
    if isstring(Argument)
        varargin(a)=[];
        switch Argument
            case "NullValue"
                NullValue=varargin{a};
            case "SizeOneCopy"
                SizeOneCopy=varargin{a};
        end
        varargin(a)=[];
    else
        a=a+1;
    end
end
Sizer=zeros(1,1);
for a=1:length(varargin)
    Sizes=num2cell(size(varargin{a}));
    Sizer(Sizes{:})=0;
end
ArraySize=size(Sizer);
if SizeOneCopy
    varargin=cellfun(@(Array)Soc(Array,ArraySize),varargin,"UniformOutput",false);
end
Output=cellfun(@ArrayFill,varargin,"UniformOutput",false);
if nargout>1
    varargout=Output;
else
    varargout={Output};
end
    function Array=ArrayFill(Array)
        Array=ArrayExpand(Array,ArraySize);
        Array(~HasValueLogical(Array))=NullValue;
    end
    function Array=HasValueLogical(Array)
        Array(:)=1;
        Array=ArrayExpand(logical(Array),ArraySize);
    end
end
function Array=ArrayExpand(Array,Sizes)
%扩展并返回数组，0填充。
if length(Sizes)>ndims(Array)||any(Sizes>size(Array))
    Sizes=num2cell(Sizes);
    Array(Sizes{:})=0;
end
end
function Array=Soc(Array,Sizes)
Sizes(size(Array)>1)=1;
Array=repmat(Array,Sizes);
end
