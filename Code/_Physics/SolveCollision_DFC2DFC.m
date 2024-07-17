function [DFC1,DFC2] = SolveCollision_DFC2DFC(DFC1,DFC2)
%% Verify Contours interacting
    nVertexs1 = size(DFC1.contour.XYZ,1);
    nVertexs2 = size(DFC2.contour.XYZ,1);
    % Filling contour position
    % Updating Spherical coordinates    
    % [azimuth,elevation,r] = cart2sph(X,Y,Z)  
    dfcRadialSize1 = DFC1.radialSize;
    dfcRadialSize2 = DFC2.radialSize;
    
    stepAngle1     = (2*pi) /nVertexs1;
    stepAngle2     = (2*pi) /nVertexs2;
    currentAngle1  = 0;
    currentAngle2  = 0;
    for indexContour1 = 1:nVertexs1
        for indexContour2 = 1:nVertexs2        
            %% Verify collision between rays
            % Define segments:
            %is of the form [x1 y1 x2 y2] where (x1,y1) is the 
            % start point and (x2,y2) is the end point of a line segment:            
            segment1 = [DFC1.center.AER(1) DFC1.center.AER(2)...
                        DFC1.contour.AER(indexContour1,1)...
                        DFC1.contour.AER(indexContour1,2)];
            segment2 = [DFC2.center.AER(1) DFC2.center.AER(2)...
                        DFC2.contour.AER(indexContour2,1)...
                        DFC2.contour.AER(indexContour2,2)];
            intData  = lineSegmentIntersect(segment1,segment2);
            %radiusUpdated1 = dfcRadialSize1;
            %radiusUpdated2 = dfcRadialSize2;
            bColliding      = intData.intAdjacencyMatrix;
            %% Correct vertex positions
            if bColliding
                % DFC1
                DFC1.contour.AER(indexContour1,1) = ...
                    intData.intMatrixX;
                    %DFC1.center.AER(1) + radiusUpdated1 * cos(currentAngle1);
                DFC1.contour.AER(indexContour1,2) = ...
                    intData.intMatrixY;
                    %DFC1.center.AER(2) + radiusUpdated1 * sin(currentAngle1);
                % DFC1
                DFC2.contour.AER(indexContour2,1) = ...
                    intData.intMatrixX;
                    %DFC2.center.AER(1) + radiusUpdated2 * cos(currentAngle2);
                DFC2.contour.AER(indexContour2,2) = ...
                    intData.intMatrixY;
                    %DFC2.center.AER(2) + radiusUpdated2 * sin(currentAngle2);
            end            
            % Updating angle 2
            currentAngle2 = currentAngle2 + stepAngle2;
        end
        % Updating angle 1
        currentAngle1 = currentAngle1 + stepAngle1;
    end
    
    %% Updating Cartesian coordinates
    % DFC1
    [dummyX,dummyY,dummyZ] = sph2cart(...
                                DFC1.contour.AER(:,1),...
                                DFC1.contour.AER(:,2),...
                                DFC1.contour.AER(:,3));
    DFC1.contour.XYZ    = [dummyX,dummyY,dummyZ]; 
    % DFC2
    [dummyX,dummyY,dummyZ] = sph2cart(...
                                DFC2.contour.AER(:,1),...
                                DFC2.contour.AER(:,2),...
                                DFC2.contour.AER(:,3));
    DFC2.contour.XYZ    = [dummyX,dummyY,dummyZ]; 
end

