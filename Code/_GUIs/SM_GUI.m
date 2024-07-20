function varargout = SM_GUI(varargin)
% SM_GUI MATLAB code for SM_GUI.fig
%      SM_GUI, by itself, creates a new SM_GUI or raises the existing
%      singleton*.
%
%      H = SM_GUI returns the handle to a new SM_GUI or the handle to
%      the existing singleton*.
%
%      SM_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SM_GUI.M with the given input arguments.
%
%      SM_GUI('Property','Value',...) creates a new SM_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before SM_GUI_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to SM_GUI_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help SM_GUI

% Last Modified by GUIDE v2.5 18-Jul-2014 08:40:51

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @SM_GUI_OpeningFcn, ...
                   'gui_OutputFcn',  @SM_GUI_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT
end

% --- Executes just before SM_GUI is made visible.
function SM_GUI_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to SM_GUI (see VARARGIN)

% Choose default command line output for SM_GUI
handles.output = hObject;

%% Requiered Data for realistic simulation 

% Embryo Params
handles.embryoData.embryo.radius = 1000;
% DFC paramas
handles.embryoData.layerDFC.nDFCs = 24;
% Mean radial size for initialize DFCs, in radians
handles.embryoData.layerDFC.radialSize   = pi/64;%((pi/2)/(nDFCs/2))/2;
handles.embryoData.layerDFC.nVertexsDFC  = 200;
handles.embryoData.layerDFC.minAzimuth   = -3*pi/4;%- pi/4;
handles.embryoData.layerDFC.maxAzimuth   = ...
                handles.embryoData.layerDFC.minAzimuth...
                + pi/4;
handles.embryoData.layerDFC.maxElevation =  pi/4;
  
% EVL params
handles.embryoData.layerEVL.nVertexs = 10;
% velocity per iteration for margin in spheric coordinates
handles.embryoData.layerEVL.marginVelocity.AER = [0,-(pi/2)*(1/200),0];

%% Create Enviroment 
handles.enviroment = CreateEnviroment(handles.embryoData);

%% Basic PLot functions
%figure(handles.mainGraphic)
axes(handles.mainGraphic);
set(handles.mainGraphic,'visible','off')
 set(gca,'XtickLabel',[],'YtickLabel',[]);
rotate3d on
[xSphere,ySphere,zSphere] = sphere;
hSurface = ...
  surf(handles.embryoData.embryo.radius.*xSphere,...
       handles.embryoData.embryo.radius.*ySphere,...
       handles.embryoData.embryo.radius.*zSphere); 
set(hSurface, 'FaceColor',[0 1 0], 'FaceAlpha',0.5, 'EdgeAlpha', 0);
%set(hSurface,'FaceColor',[0 1 0],'FaceAlpha',0.5);

DrawDFCLayer(handles.enviroment.layerDFC,1);


% Update handles structure
guidata(hObject, handles);

% UIWAIT makes SM_GUI wait for user response (see UIRESUME)
% uiwait(handles.figure1);
end



% --- Outputs from this function are returned to the command line.
function varargout = SM_GUI_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
end

% --- Executes on button press in tbPause.
function tbPause_Callback(hObject, eventdata, handles)
% hObject    handle to tbPause (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of tbPause
    if get(hObject,'Value') == 1 && ...
       get(handles.tbRUN,'Value') == 1
            set(handles.tbRUN,'Value',0);

            % Update handles structure
            guidata(hObject, handles);            
    end
end

% --- Executes on button press in tbRUN.
function tbRUN_Callback(hObject, eventdata, handles)
% hObject    handle to tbRUN (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of tbRUN
%% Loop of migration
set(handles.tbPause,'Value',0);
% Update handles structure
guidata(hObject, handles);
        while get(handles.tbPause,'Value') == 0
            handles.enviroment = UpdateLayers(handles.enviroment);

            % Draw Section
            pause(0.01)
            hold off
            rotate3d on
            [xSphere,ySphere,zSphere] = sphere;
            hSurface = ...
              surf(handles.embryoData.embryo.radius.*xSphere,...
                   handles.embryoData.embryo.radius.*ySphere,...
                   handles.embryoData.embryo.radius.*zSphere); 
            set(hSurface, 'FaceColor',[0 1 0], 'FaceAlpha',0.5, 'EdgeAlpha', 0);

            DrawDFCLayer(handles.enviroment.layerDFC,1);
            % Update handles structure
            guidata(hObject, handles);
        end
end

% --- Executes on selection change in pmMenuSave.
function pmMenuSave_Callback(hObject, eventdata, handles)
% hObject    handle to pmMenuSave (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmMenuSave contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmMenuSave
end

% --- Executes during object creation, after setting all properties.
function pmMenuSave_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmMenuSave (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

end